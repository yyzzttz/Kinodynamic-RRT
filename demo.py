#!/usr/bin/env python3
"""
Demo script for Kinodynamic RRT Planner
Demonstrates path planning for a planar hover-craft robot in PyBullet
"""

import time
import numpy as np
from kinodynamic_rrt import KinodynamicRRT, State
from robot_simulator import RobotSimulator
from visualization import plot_search_tree, create_trajectory_video


def create_environment():
    """Create an interesting environment with obstacles"""
    # Define obstacles: (x, y, radius)
    # Arranged to create an interesting but solvable maze-like environment
    obstacles = [
        (3, 2, 0.6),    # Lower left area
        (5, 3, 0.5),    # Middle lower
        (2, 5, 0.6),    # Left middle
        (6, 5, 0.5),    # Center
        (4, 7, 0.5),    # Upper middle
        (7, 7, 0.4),    # Upper right area
        (8, 5, 0.5),    # Right middle
    ]
    
    return obstacles


def evaluate_primitives():
    """Evaluate performance with different numbers of motion primitives"""
    print("=" * 60)
    print("Evaluating performance with different motion primitives")
    print("=" * 60)
    
    # Environment setup
    obstacles = create_environment()
    bounds = ((0, 10), (0, 10))
    start_state = State(1, 1, 0, 0, 0, 0)
    goal_region = (9, 9, 0.8)  # Larger goal region for easier success
    
    # Test different numbers of primitives
    num_primitives_list = [4, 8, 16, 32]
    results = []
    
    for num_primitives in num_primitives_list:
        print(f"\nTesting with {num_primitives} motion primitives...")
        
        # Create simulator for collision checking
        sim = RobotSimulator(obstacles, gui=False)
        
        # Create collision checker function
        def collision_checker(state):
            return sim.check_collision(state)
        
        # Create planner
        rrt = KinodynamicRRT(
            start_state=start_state,
            goal_region=goal_region,
            bounds=bounds,
            dt=0.1,
            max_control_effort=2.0,
            goal_eps_pos=0.5,
            goal_eps_vel=0.3,
            max_iters=3000,
            num_primitives=num_primitives
        )
        
        # Plan
        start_time = time.time()
        success = rrt.plan(collision_checker)
        planning_time = time.time() - start_time
        
        # Calculate path quality metrics
        path_length = 0
        if success and rrt.path:
            path_states = rrt.get_path_states()
            for i in range(1, len(path_states)):
                dx = path_states[i].x - path_states[i-1].x
                dy = path_states[i].y - path_states[i-1].y
                path_length += np.sqrt(dx**2 + dy**2)
        
        results.append({
            'num_primitives': num_primitives,
            'success': success,
            'planning_time': planning_time,
            'num_nodes': len(rrt.nodes),
            'path_length': path_length if success else None
        })
        
        print(f"  Success: {success}")
        print(f"  Planning time: {planning_time:.2f} seconds")
        print(f"  Nodes in tree: {len(rrt.nodes)}")
        if success:
            print(f"  Path length: {path_length:.2f} m")
        
        sim.close()
    
    # Print summary
    print("\n" + "=" * 60)
    print("Summary of Results")
    print("=" * 60)
    print(f"{'Primitives':<12} {'Success':<10} {'Time (s)':<12} {'Nodes':<10} {'Path Length (m)':<15}")
    print("-" * 60)
    for r in results:
        path_len_str = f"{r['path_length']:.2f}" if r['path_length'] else "N/A"
        print(f"{r['num_primitives']:<12} {str(r['success']):<10} {r['planning_time']:<12.2f} {r['num_nodes']:<10} {path_len_str:<15}")
    
    return results


def main():
    """Main demo function"""
    print("=" * 60)
    print("Kinodynamic RRT Planner Demo")
    print("=" * 60)
    
    # Expected runtime
    print("\nExpected runtime: 2-5 minutes")
    print("(This includes planning, visualization, and video generation)")
    print("Note: Video generation may take additional time if ffmpeg is available\n")
    
    # Create environment
    obstacles = create_environment()
    bounds = ((0, 10), (0, 10))
    start_state = State(1, 1, 0, 0, 0, 0)
    goal_region = (9, 9, 0.8)  # Larger goal region for easier success
    
    # Create simulator
    print("Creating simulation environment...")
    sim = RobotSimulator(obstacles, gui=False)
    
    # Create collision checker
    def collision_checker(state):
        return sim.check_collision(state)
    
    # Create planner with optimal number of primitives (based on evaluation)
    print("Initializing Kinodynamic RRT planner...")
    num_primitives = 8  # Good balance between performance and computation
    rrt = KinodynamicRRT(
        start_state=start_state,
        goal_region=goal_region,
        bounds=bounds,
        dt=0.1,
        max_control_effort=2.0,
        goal_eps_pos=0.5,
        goal_eps_vel=0.5,  # More lenient velocity tolerance
        max_iters=8000,    # More iterations for reliability
        num_primitives=num_primitives
    )
    
    # Plan
    print(f"Planning with {num_primitives} motion primitives...")
    print("This may take a moment...")
    demo_start_time = time.time()
    planning_start = time.time()
    success = rrt.plan(collision_checker)
    planning_time = time.time() - planning_start
    
    if success:
        print(f"\n✓ Path found in {planning_time:.2f} seconds!")
        print(f"  Tree nodes: {len(rrt.nodes)}")
        
        path_states = rrt.get_path_states()
        path_length = 0
        for i in range(1, len(path_states)):
            dx = path_states[i].x - path_states[i-1].x
            dy = path_states[i].y - path_states[i-1].y
            path_length += np.sqrt(dx**2 + dy**2)
        print(f"  Path length: {path_length:.2f} m")
    else:
        print(f"\n✗ Path not found after {planning_time:.2f} seconds")
        print("  Try increasing max_iters or adjusting parameters")
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    
    # Search tree image
    print("  Creating search tree visualization...")
    plot_search_tree(rrt, obstacles, goal_region, bounds, 
                    filename='search_tree.png')
    
    if success:
        # Trajectory video
        print("  Creating trajectory execution video...")
        create_trajectory_video(rrt, obstacles, goal_region, bounds,
                              filename='trajectory.mp4', fps=30)
    
    # Performance evaluation
    print("\n" + "=" * 60)
    print("Running performance evaluation...")
    print("=" * 60)
    evaluate_primitives()
    
    # Cleanup
    sim.close()
    
    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
    print("Output files:")
    print("  - search_tree.png: Visualization of the search tree")
    if success:
        print("  - trajectory.mp4: Video of trajectory execution")
    total_time = time.time() - demo_start_time
    print("\nTotal runtime: {:.2f} seconds".format(total_time))


if __name__ == "__main__":
    main()

