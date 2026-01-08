"""
Visualization utilities for Kinodynamic RRT
Generates search tree images and trajectory videos
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np
import math


def plot_search_tree(rrt, obstacles, goal_region, bounds, filename='search_tree.png'):
    """Plot the RRT search tree"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Draw obstacles
    for obs_x, obs_y, obs_r in obstacles:
        circle = patches.Circle((obs_x, obs_y), obs_r, 
                               color='red', alpha=0.6, zorder=1)
        ax.add_patch(circle)
    
    # Draw goal region
    goal_x, goal_y, goal_r = goal_region
    goal_circle = patches.Circle((goal_x, goal_y), goal_r, 
                                color='green', alpha=0.4, zorder=2)
    ax.add_patch(goal_circle)
    
    # Draw tree
    for node in rrt.nodes:
        if node.parent is not None:
            # Draw edge
            ax.plot([node.parent.state.x, node.state.x],
                   [node.parent.state.y, node.state.y],
                   'b-', linewidth=0.5, alpha=0.6, zorder=0)
        
        # Draw node
        ax.plot(node.state.x, node.state.y, 'ko', 
               markersize=2, zorder=3)
    
    # Draw path if found
    if rrt.path:
        path_states = rrt.get_path_states()
        if path_states:
            path_x = [s.x for s in path_states]
            path_y = [s.y for s in path_states]
            ax.plot(path_x, path_y, 'g-', linewidth=3, 
                   label='Path', zorder=4)
    
    # Draw start
    ax.plot(rrt.start_state.x, rrt.start_state.y, 'go', 
           markersize=10, label='Start', zorder=5)
    
    # Draw goal center
    ax.plot(goal_x, goal_y, 'r*', markersize=15, 
           label='Goal', zorder=5)
    
    ax.set_xlim(bounds[0][0] - 1, bounds[0][1] + 1)
    ax.set_ylim(bounds[1][0] - 1, bounds[1][1] + 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title(f'Kinodynamic RRT Search Tree (Nodes: {len(rrt.nodes)})')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    print(f"Search tree saved to {filename}")
    plt.close()


def create_trajectory_video(rrt, obstacles, goal_region, bounds, 
                           filename='trajectory.mp4', fps=30):
    """Create video of trajectory execution"""
    if not rrt.path:
        print("No path found, cannot create video")
        return
    
    path_states = rrt.get_path_states()
    if not path_states:
        print("No path states, cannot create video")
        return
    
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Draw obstacles
    for obs_x, obs_y, obs_r in obstacles:
        circle = patches.Circle((obs_x, obs_y), obs_r, 
                               color='red', alpha=0.6)
        ax.add_patch(circle)
    
    # Draw goal region
    goal_x, goal_y, goal_r = goal_region
    goal_circle = patches.Circle((goal_x, goal_y), goal_r, 
                                color='green', alpha=0.4)
    ax.add_patch(goal_circle)
    
    # Draw start and goal
    ax.plot(rrt.start_state.x, rrt.start_state.y, 'go', 
           markersize=10, label='Start')
    ax.plot(goal_x, goal_y, 'r*', markersize=15, label='Goal')
    
    ax.set_xlim(bounds[0][0] - 1, bounds[0][1] + 1)
    ax.set_ylim(bounds[1][0] - 1, bounds[1][1] + 1)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('X (m)')
    ax.set_ylabel('Y (m)')
    ax.set_title('Robot Trajectory Execution')
    ax.legend()
    
    # Robot representation
    robot_circle = patches.Circle((0, 0), 0.3, color='blue', alpha=0.7)
    ax.add_patch(robot_circle)
    
    # Trajectory line
    traj_line, = ax.plot([], [], 'g-', linewidth=2, alpha=0.5)
    
    # Store arrow reference
    robot_arrow = [None]
    
    def animate(frame):
        if frame >= len(path_states):
            return [robot_circle, traj_line]
        
        state = path_states[frame]
        
        # Update robot position
        robot_circle.center = (state.x, state.y)
        
        # Update robot orientation arrow
        arrow_length = 0.5
        dx = arrow_length * math.cos(state.theta)
        dy = arrow_length * math.sin(state.theta)
        
        # Remove old arrow if exists
        if robot_arrow[0] is not None:
            robot_arrow[0].remove()
        
        # Create new arrow
        robot_arrow[0] = ax.arrow(state.x, state.y, dx, dy, 
                                  head_width=0.2, head_length=0.1,
                                  fc='darkblue', ec='darkblue')
        
        # Update trajectory line
        if frame > 0:
            traj_x = [s.x for s in path_states[:frame+1]]
            traj_y = [s.y for s in path_states[:frame+1]]
            traj_line.set_data(traj_x, traj_y)
        
        return [robot_circle, traj_line]
    
    # Create animation
    num_frames = len(path_states)
    anim = FuncAnimation(fig, animate, frames=num_frames, 
                        interval=1000/fps, blit=False, repeat=True)
    
    # Save video (try mp4 first, fall back to gif)
    print(f"Creating trajectory video...")
    try:
        anim.save(filename, writer='ffmpeg', fps=fps, bitrate=1800)
        print(f"Trajectory video saved to {filename}")
    except Exception as e:
        # Fall back to gif if ffmpeg not available
        gif_filename = filename.replace('.mp4', '.gif')
        print(f"ffmpeg not available, saving as GIF instead...")
        try:
            anim.save(gif_filename, writer='pillow', fps=fps)
            print(f"Trajectory animation saved to {gif_filename}")
        except Exception as e2:
            print(f"Warning: Could not save animation ({e2})")
            print("Saving static final frame instead...")
            # Save final frame
            animate(num_frames - 1)
            static_filename = filename.replace('.mp4', '_final.png')
            plt.savefig(static_filename, dpi=150, bbox_inches='tight')
            print(f"Final frame saved to {static_filename}")
    
    plt.close()

