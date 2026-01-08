"""
Kinodynamic RRT Implementation for Planar Hover-craft Robot
Robot can accelerate/decelerate in x, y, and theta dimensions
"""

import numpy as np
import pybullet as p
import pybullet_data
import math
import random
from collections import deque


class State:
    """Robot state: position (x, y, theta) and velocity (vx, vy, vtheta)"""
    def __init__(self, x=0, y=0, theta=0, vx=0, vy=0, vtheta=0):
        self.x = x
        self.y = y
        self.theta = theta
        self.vx = vx
        self.vy = vy
        self.vtheta = vtheta
    
    def to_array(self):
        return np.array([self.x, self.y, self.theta, self.vx, self.vy, self.vtheta])
    
    @classmethod
    def from_array(cls, arr):
        return cls(arr[0], arr[1], arr[2], arr[3], arr[4], arr[5])
    
    def copy(self):
        return State(self.x, self.y, self.theta, self.vx, self.vy, self.vtheta)


class Node:
    """Tree node containing state and trajectory"""
    def __init__(self, state, parent=None, trajectory=None, control=None):
        self.state = state
        self.parent = parent
        self.trajectory = trajectory if trajectory is not None else []
        self.control = control  # control input that led to this node
        self.children = []


class KinodynamicRRT:
    """Kinodynamic RRT planner for planar hover-craft robot"""
    
    def __init__(self, 
                 start_state, 
                 goal_region, 
                 bounds, 
                 dt=0.1, 
                 max_control_effort=2.0,
                 goal_eps_pos=0.5,
                 goal_eps_vel=0.3,
                 max_iters=5000,
                 num_primitives=8):
        """
        Args:
            start_state: State object for start
            goal_region: (center_x, center_y, radius) for goal region
            bounds: ((x_min, x_max), (y_min, y_max)) for sampling bounds
            dt: time step for trajectory propagation
            max_control_effort: maximum acceleration in each dimension
            goal_eps_pos: position tolerance for goal
            goal_eps_vel: velocity tolerance for goal
            max_iters: maximum iterations
            num_primitives: number of motion primitives to try
        """
        self.start_state = start_state
        self.goal_region = goal_region
        self.bounds = bounds
        self.dt = dt
        self.max_control_effort = max_control_effort
        self.goal_eps_pos = goal_eps_pos
        self.goal_eps_vel = goal_eps_vel
        self.max_iters = max_iters
        self.num_primitives = num_primitives
        
        # Initialize tree
        self.root = Node(start_state)
        self.nodes = [self.root]
        self.path = None
        
        # Motion primitives: (ax, ay, atheta) - accelerations
        self._generate_motion_primitives()
    
    def _generate_motion_primitives(self):
        """Generate motion primitives (control inputs)"""
        self.primitives = []
        
        # Generate uniformly distributed primitives
        # Use spherical-like distribution for better coverage
        n_per_dim = max(2, int(np.cbrt(self.num_primitives)))
        
        for ax in np.linspace(-self.max_control_effort, self.max_control_effort, n_per_dim):
            for ay in np.linspace(-self.max_control_effort, self.max_control_effort, n_per_dim):
                # Simpler theta control
                self.primitives.append((ax, ay, 0))
        
        # Add some with rotation
        for ax in np.linspace(-self.max_control_effort, self.max_control_effort, 3):
            for ay in np.linspace(-self.max_control_effort, self.max_control_effort, 3):
                for atheta in [-self.max_control_effort * 0.5, self.max_control_effort * 0.5]:
                    self.primitives.append((ax, ay, atheta))
        
        # Remove duplicates and limit to num_primitives
        seen = set()
        unique_primitives = []
        for p in self.primitives:
            key = (round(p[0], 2), round(p[1], 2), round(p[2], 2))
            if key not in seen:
                seen.add(key)
                unique_primitives.append(p)
        
        self.primitives = unique_primitives[:self.num_primitives]
        
        # Ensure we have enough primitives
        while len(self.primitives) < self.num_primitives:
            ax = random.uniform(-self.max_control_effort, self.max_control_effort)
            ay = random.uniform(-self.max_control_effort, self.max_control_effort)
            atheta = random.uniform(-self.max_control_effort * 0.3, self.max_control_effort * 0.3)
            self.primitives.append((ax, ay, atheta))
    
    def _distance(self, state1, state2):
        """Compute distance between two states (weighted position and velocity)"""
        pos_diff = np.array([state1.x - state2.x, state1.y - state2.y, 
                            self._angle_diff(state1.theta, state2.theta)])
        vel_diff = np.array([state1.vx - state2.vx, state1.vy - state2.vy, 
                            state1.vtheta - state2.vtheta])
        
        # Weight position more than velocity
        pos_dist = np.linalg.norm(pos_diff)
        vel_dist = np.linalg.norm(vel_diff)
        return pos_dist + 0.3 * vel_dist
    
    def _angle_diff(self, a1, a2):
        """Compute angular difference"""
        diff = a1 - a2
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        return diff
    
    def _nearest_node(self, target_state):
        """Find nearest node in tree to target state"""
        min_dist = float('inf')
        nearest = None
        
        for node in self.nodes:
            dist = self._distance(node.state, target_state)
            if dist < min_dist:
                min_dist = dist
                nearest = node
        
        return nearest
    
    def _propagate(self, state, control, dt, num_steps=10):
        """
        Propagate state forward using dynamics
        Dynamics: double integrator with acceleration control
        """
        trajectory = [state.copy()]
        current_state = state.copy()
        
        max_vel = 3.0  # Maximum velocity limit
        max_vtheta = 2.0  # Maximum angular velocity
        
        for _ in range(num_steps):
            # Update velocities with limits
            current_state.vx += control[0] * dt
            current_state.vy += control[1] * dt
            current_state.vtheta += control[2] * dt
            
            # Clamp velocities
            current_state.vx = np.clip(current_state.vx, -max_vel, max_vel)
            current_state.vy = np.clip(current_state.vy, -max_vel, max_vel)
            current_state.vtheta = np.clip(current_state.vtheta, -max_vtheta, max_vtheta)
            
            # Update positions
            current_state.x += current_state.vx * dt
            current_state.y += current_state.vy * dt
            current_state.theta += current_state.vtheta * dt
            
            # Normalize angle
            current_state.theta = math.atan2(math.sin(current_state.theta), 
                                            math.cos(current_state.theta))
            
            trajectory.append(current_state.copy())
        
        return trajectory
    
    def _check_bounds(self, state):
        """Check if state is within bounds"""
        if state.x < self.bounds[0][0] or state.x > self.bounds[0][1]:
            return False
        if state.y < self.bounds[1][0] or state.y > self.bounds[1][1]:
            return False
        return True
    
    def _check_collision(self, trajectory, collision_checker):
        """Check if trajectory collides with obstacles or goes out of bounds"""
        for state in trajectory:
            # Check bounds first
            if not self._check_bounds(state):
                return True
            # Check collision with obstacles
            if collision_checker is not None and collision_checker(state):
                return True
        return False
    
    def _sample_state(self):
        """Sample random state in bounds"""
        x = random.uniform(self.bounds[0][0], self.bounds[0][1])
        y = random.uniform(self.bounds[1][0], self.bounds[1][1])
        theta = random.uniform(-math.pi, math.pi)
        vx = random.uniform(-1.0, 1.0)
        vy = random.uniform(-1.0, 1.0)
        vtheta = random.uniform(-0.5, 0.5)
        return State(x, y, theta, vx, vy, vtheta)
    
    def _extend(self, target_state, collision_checker):
        """Extend tree towards target state using motion primitives"""
        nearest_node = self._nearest_node(target_state)
        
        best_node = None
        best_dist = float('inf')
        valid_nodes = []
        
        # Try all motion primitives and collect valid ones
        for primitive in self.primitives:
            trajectory = self._propagate(nearest_node.state, primitive, self.dt)
            
            # Check collision
            if self._check_collision(trajectory, collision_checker):
                continue
            
            # Check if this gets us closer to target
            final_state = trajectory[-1]
            dist = self._distance(final_state, target_state)
            
            valid_nodes.append((dist, final_state, trajectory, primitive))
            
            if dist < best_dist:
                best_dist = dist
                best_node = Node(final_state, parent=nearest_node, 
                               trajectory=trajectory, control=primitive)
        
        # If we have valid nodes but best one doesn't improve much,
        # occasionally pick a random valid one for exploration
        if valid_nodes and random.random() < 0.1:
            _, final_state, trajectory, primitive = random.choice(valid_nodes)
            best_node = Node(final_state, parent=nearest_node,
                           trajectory=trajectory, control=primitive)
        
        if best_node is None:
            return None
        
        # Add to tree
        nearest_node.children.append(best_node)
        self.nodes.append(best_node)
        
        return best_node
    
    def _reached_goal(self, state):
        """Check if state is in goal region"""
        goal_x, goal_y, goal_r = self.goal_region
        pos_dist = math.sqrt((state.x - goal_x)**2 + (state.y - goal_y)**2)
        vel_dist = math.sqrt(state.vx**2 + state.vy**2)
        
        # More lenient goal checking - only check position and linear velocity
        return pos_dist < goal_r + self.goal_eps_pos and vel_dist < self.goal_eps_vel * 2
    
    def plan(self, collision_checker):
        """Main planning loop"""
        for iteration in range(self.max_iters):
            # Sample random state with higher goal bias
            rand_val = random.random()
            if rand_val < 0.2:  # 20% bias towards goal
                goal_x, goal_y, _ = self.goal_region
                target_state = State(goal_x, goal_y, 0, 0, 0, 0)
            elif rand_val < 0.3:  # 10% bias towards goal with some randomness
                goal_x, goal_y, _ = self.goal_region
                target_state = State(
                    goal_x + random.uniform(-1, 1),
                    goal_y + random.uniform(-1, 1),
                    0, 0, 0, 0
                )
            else:
                target_state = self._sample_state()
            
            # Extend towards target
            new_node = self._extend(target_state, collision_checker)
            
            if new_node is None:
                continue
            
            # Check if goal reached
            if self._reached_goal(new_node.state):
                self.path = self._backtrace_path(new_node)
                return True
        
        return False
    
    def _backtrace_path(self, node):
        """Backtrace path from goal node to start"""
        path = []
        current = node
        
        while current is not None:
            path.append(current)
            current = current.parent
        
        path.reverse()
        return path
    
    def get_path_states(self):
        """Get sequence of states along the path"""
        if self.path is None:
            return []
        
        states = []
        for node in self.path:
            if node.trajectory:
                states.extend(node.trajectory)
            else:
                states.append(node.state)
        
        return states

