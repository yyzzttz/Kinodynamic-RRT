"""
Robot Simulator for PyBullet
Creates a simple box robot and environment with obstacles
"""

import pybullet as p
import pybullet_data
import numpy as np
import math


class RobotSimulator:
    """PyBullet simulation environment for hover-craft robot"""
    
    def __init__(self, obstacles, gui=True):
        """
        Args:
            obstacles: list of (x, y, radius) tuples
            gui: whether to show GUI
        """
        self.obstacles = obstacles
        self.obstacle_ids = []
        self.robot_id = None
        
        # Start PyBullet
        if gui:
            self.client = p.connect(p.GUI)
            p.configureDebugVisualizer(p.COV_ENABLE_GUI, 0)
        else:
            self.client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        p.setGravity(0, 0, 0)  # No gravity for hover-craft
        
        # Create ground plane
        plane_id = p.loadURDF("plane.urdf")
        
        # Create obstacles
        self._create_obstacles()
        
        # Create robot (simple box)
        self._create_robot()
    
    def _create_obstacles(self):
        """Create cylindrical obstacles"""
        for obs_x, obs_y, obs_r in self.obstacles:
            # Create a cylinder obstacle
            visual_shape = p.createVisualShape(
                shapeType=p.GEOM_CYLINDER,
                radius=obs_r,
                length=1.0,
                rgbaColor=[0.7, 0.3, 0.3, 1.0]
            )
            collision_shape = p.createCollisionShape(
                shapeType=p.GEOM_CYLINDER,
                radius=obs_r,
                height=1.0
            )
            obstacle_id = p.createMultiBody(
                baseMass=0,
                baseCollisionShapeIndex=collision_shape,
                baseVisualShapeIndex=visual_shape,
                basePosition=[obs_x, obs_y, 0.5]
            )
            self.obstacle_ids.append(obstacle_id)
    
    def _create_robot(self):
        """Create a simple box robot"""
        # Robot dimensions
        robot_size = 0.3
        
        visual_shape = p.createVisualShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[robot_size/2, robot_size/2, robot_size/2],
            rgbaColor=[0.3, 0.7, 0.9, 1.0]
        )
        collision_shape = p.createCollisionShape(
            shapeType=p.GEOM_BOX,
            halfExtents=[robot_size/2, robot_size/2, robot_size/2]
        )
        
        self.robot_id = p.createMultiBody(
            baseMass=1.0,
            baseCollisionShapeIndex=collision_shape,
            baseVisualShapeIndex=visual_shape,
            basePosition=[0, 0, 0.15]
        )
    
    def set_robot_state(self, state):
        """Set robot position and orientation"""
        # Position
        pos = [state.x, state.y, 0.15]
        # Orientation (quaternion from euler)
        orn = p.getQuaternionFromEuler([0, 0, state.theta])
        p.resetBasePositionAndOrientation(self.robot_id, pos, orn)
    
    def check_collision(self, state):
        """Check if robot at state collides with obstacles"""
        # Set robot to this state temporarily
        pos = [state.x, state.y, 0.15]
        orn = p.getQuaternionFromEuler([0, 0, state.theta])
        p.resetBasePositionAndOrientation(self.robot_id, pos, orn)
        
        # Check collisions
        for obs_id in self.obstacle_ids:
            contacts = p.getContactPoints(self.robot_id, obs_id)
            if len(contacts) > 0:
                return True
        
        return False
    
    def visualize_path(self, path_states, delay=0.01):
        """Visualize path execution"""
        for state in path_states:
            self.set_robot_state(state)
            p.stepSimulation()
            if delay > 0:
                import time
                time.sleep(delay)
    
    def draw_tree(self, nodes):
        """Draw RRT tree in PyBullet"""
        line_ids = []
        for node in nodes:
            if node.parent is not None:
                start_pos = [node.parent.state.x, node.parent.state.y, 0.2]
                end_pos = [node.state.x, node.state.y, 0.2]
                line_id = p.addUserDebugLine(
                    start_pos, end_pos,
                    lineColorRGB=[0.5, 0.5, 0.5],
                    lineWidth=2
                )
                line_ids.append(line_id)
        return line_ids
    
    def draw_goal_region(self, goal_region):
        """Draw goal region"""
        goal_x, goal_y, goal_r = goal_region
        # Draw circle
        num_points = 32
        points = []
        for i in range(num_points + 1):
            angle = 2 * math.pi * i / num_points
            x = goal_x + goal_r * math.cos(angle)
            y = goal_y + goal_r * math.sin(angle)
            points.append([x, y, 0.1])
        
        for i in range(len(points) - 1):
            p.addUserDebugLine(
                points[i], points[i+1],
                lineColorRGB=[0, 1, 0],
                lineWidth=3
            )
    
    def close(self):
        """Close PyBullet connection"""
        p.disconnect(self.client)

