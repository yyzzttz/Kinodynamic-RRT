# Kinodynamic RRT Path Planning for Planar Hover-craft Robot

A comprehensive implementation of the Kinodynamic Rapidly-exploring Random Tree (RRT) algorithm for path planning of a planar hover-craft robot with dynamic constraints. This project extends the classical RRT algorithm to operate in the full state space (position and velocity) rather than just configuration space, ensuring that planned trajectories are both collision-free and dynamically feasible.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Algorithm Description](#algorithm-description)
- [Results](#results)
- [Technical Details](#technical-details)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

This project implements a Kinodynamic RRT planner for a planar hover-craft robot that can accelerate and decelerate in the x, y, and θ (orientation) dimensions. Unlike geometric path planning algorithms, this implementation considers the robot's dynamics, including velocity and acceleration constraints, ensuring that generated paths are executable by real robots.

### Key Contributions

- **Full State Space Planning**: Operates in 6-dimensional state space (position + velocity)
- **Dynamic Feasibility**: All trajectories respect velocity and acceleration constraints
- **Motion Primitives**: Configurable discrete control inputs for trajectory generation
- **Physics-Based Collision Detection**: Uses PyBullet for accurate collision checking
- **Performance Evaluation**: Comprehensive analysis of different motion primitive configurations

## Features

- ✅ **Kinodynamic RRT Algorithm**: Full implementation with state-space exploration
- ✅ **PyBullet Integration**: Realistic physics simulation and collision detection
- ✅ **Motion Primitives**: Configurable number of control inputs (4, 8, 16, 32)
- ✅ **Visualization**: Search tree visualization and trajectory animation
- ✅ **Performance Analysis**: Automated evaluation of different algorithm configurations
- ✅ **Modular Design**: Clean, well-documented code structure

## System Requirements

### Required Software

- **Python 3.7+** (Python 3.8 or higher recommended)
- **PyBullet** (physics simulation engine)
- **NumPy** (numerical computations)
- **Matplotlib** (visualization)
- **SciPy** (scientific computing, optional)
- **Pillow** (image processing for GIF generation)

### Operating System

- **Linux** (Ubuntu 18.04+ recommended)
- **macOS** (10.14+)
- **Windows** (10+, with WSL recommended)

### Hardware

- Minimum 4GB RAM
- Graphics card recommended for visualization (optional)

## Installation

### Quick Start

1. **Clone or download the project**:
   ```bash
   cd /path/to/Final_Project
   ```

2. **Run the installation script**:
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

   This will install required Python packages (scipy, pillow).

   **Note**: PyBullet, Python 3, NumPy, and Matplotlib are assumed to be pre-installed. If not, install them first:
   ```bash
   pip3 install pybullet numpy matplotlib
   ```

### Manual Installation

If you prefer manual installation:

```bash
pip3 install scipy pillow --user
```

### Verification

To verify the installation, run:

```bash
python3 -c "import pybullet, numpy, matplotlib; print('All packages installed successfully!')"
```

## Usage

### Basic Usage

Run the main demo script:

```bash
python3 demo.py
```

This will:
1. Perform path planning with the default configuration
2. Generate a search tree visualization (`search_tree.png`)
3. Create a trajectory execution animation (`trajectory.gif` or `trajectory.mp4`)
4. Evaluate performance with different numbers of motion primitives

### Expected Runtime

The demo typically takes **2-5 minutes** to complete, including:
- Path planning (~0.3-10 seconds depending on configuration)
- Visualization generation (~10-30 seconds)
- Performance evaluation (~20-60 seconds)

### Output Files

After running `demo.py`, you will find:

- `search_tree.png`: Visualization of the RRT search tree with obstacles, goal region, and final path
- `trajectory.gif` or `trajectory.mp4`: Animation of the robot executing the planned trajectory
- Console output: Performance metrics and evaluation results

### Customization

You can modify the following parameters in `demo.py`:

```python
# Environment configuration
obstacles = [...]  # List of (x, y, radius) tuples
bounds = ((0, 10), (0, 10))  # Workspace bounds
start_state = State(1, 1, 0, 0, 0, 0)  # Start position and velocity
goal_region = (9, 9, 0.8)  # Goal center and radius

# Algorithm parameters
num_primitives = 16  # Number of motion primitives
max_iters = 5000  # Maximum iterations
dt = 0.1  # Time step (seconds)
max_control_effort = 2.0  # Maximum acceleration (m/s²)
```

## Project Structure

```
Final_Project/
├── demo.py                      # Main demo script
├── kinodynamic_rrt.py           # Core RRT algorithm implementation
├── robot_simulator.py          # PyBullet simulation environment
├── visualization.py             # Visualization utilities
├── install.sh                   # Installation script
├── README.md                    # This file
│
├── Draft(English notation)/     # Algorithm documentation (English)
│   ├── RRT_Kinodynamic.txt
│   ├── Extend_kinodynamic.txt
│   ├── Connect_kinodynamic.txt
│   └── ...
│
├── Draft(chinese notation)/     # Algorithm documentation (Chinese)
│   ├── RRT_Kinodynamic.txt
│   ├── Extend_kinodynamic.txt
│   └── ...
│
└── Output files (generated):
    ├── search_tree.png          # Search tree visualization
    ├── trajectory.gif          # Trajectory animation
    └── results.txt             # Performance results
```

## Algorithm Description

### Kinodynamic RRT Overview

The Kinodynamic RRT algorithm extends classical RRT by:

1. **State Space**: Operating in full 6D state space `[x, y, θ, vₓ, vᵧ, vθ]` instead of just configuration space
2. **Motion Primitives**: Using discrete control inputs (accelerations) to generate feasible trajectories
3. **Dynamic Constraints**: Respecting velocity and acceleration limits
4. **Trajectory Validation**: Checking entire trajectories for collisions and constraint violations

### Key Components

#### 1. State Representation
```python
State(x, y, theta, vx, vy, vtheta)
```
- Position: `(x, y, θ)` in meters and radians
- Velocity: `(vₓ, vᵧ, vθ)` in m/s and rad/s

#### 2. System Dynamics
Double integrator model with acceleration control:
- `v(t+Δt) = v(t) + a·Δt`
- `q(t+Δt) = q(t) + v(t+Δt)·Δt`

#### 3. Motion Primitives
Discrete set of constant acceleration control inputs:
- `u = [aₓ, aᵧ, aθ]ᵀ`
- Uniformly distributed in control space
- Configurable number (4, 8, 16, or 32)

#### 4. Distance Metric
Weighted combination of position and velocity:
```
d(x₁, x₂) = wₚ·||q₁ - q₂|| + wᵥ·||v₁ - v₂||
```
where `wₚ = 1.0` and `wᵥ = 0.3`

### Algorithm Pseudocode

```
FUNCTION RRT_KINODYNAMIC(x_start, x_goal, dt, goal_eps, max_iters):
    1. Initialize tree T with root node at x_start
    2. FOR k = 1 TO max_iters:
        a. Sample random state x_rand
        b. Find nearest node x_near in tree
        c. For each motion primitive:
           - Propagate trajectory from x_near
           - Check collision and constraints
           - Evaluate distance to target
        d. Select best valid trajectory
        e. Add new node to tree
        f. IF reached goal: RETURN path
    3. RETURN FAILURE
```

For detailed algorithm descriptions, see the documentation files in `Draft(English notation)/`.

## Results

### Performance Metrics

The algorithm has been evaluated with different numbers of motion primitives:

| Primitives | Success Rate | Avg. Time (s) | Avg. Nodes | Path Length (m) |
|------------|--------------|---------------|------------|-----------------|
| 4          | High         | 0.60          | 451        | 16.97           |
| 8          | Medium       | 12.92         | 2946       | N/A             |
| 16         | High         | 8.65          | 2149       | 18.45           |
| 32         | High         | 3.27          | 812        | 17.89           |

### Key Findings

- **32 primitives** provides the best balance between exploration capability and computational efficiency
- More primitives enable better trajectory quality with fewer total nodes
- Success rate depends on both primitives and environment complexity

### Sample Results

With 8 motion primitives and default settings:
- **Planning time**: 0.28 seconds
- **Tree nodes**: 194
- **Path length**: 16.97 m
- **Success**: ✓

## Technical Details

### Robot Model

- **Type**: Planar hover-craft (no gravity)
- **Shape**: Box (0.3 × 0.3 × 0.3 m)
- **Dynamics**: Double integrator
- **Constraints**:
  - Maximum velocity: 3.0 m/s (linear), 2.0 rad/s (angular)
  - Maximum acceleration: 2.0 m/s²

### Environment

- **Workspace**: 10 × 10 m
- **Obstacles**: 7 cylindrical obstacles
- **Goal region**: Circle with 0.8 m radius

### Algorithm Parameters

- **Time step**: Δt = 0.1 s
- **Trajectory duration**: 1.0 s (10 steps)
- **Position tolerance**: 0.5 m
- **Velocity tolerance**: 0.5 m/s
- **Maximum iterations**: 5000-8000

## Documentation

### Algorithm Documentation

Detailed algorithm descriptions are available in:
- `Draft(English notation)/`: English documentation
- `Draft(chinese notation)/`: Chinese documentation

Key files:
- `RRT_Kinodynamic.txt`: Main algorithm description
- `Extend_kinodynamic.txt`: Extension operation
- `Connect_kinodynamic.txt`: Connect operation

### Project Report

A comprehensive project report is available:
- English version: `Draft(English notation)/project_report.tex`
- Chinese version: `Draft(chinese notation)/project_report_chinese.tex`

The report includes:
- Introduction and motivation
- Detailed implementation description
- Experimental results and analysis
- Performance evaluation

## Troubleshooting

### Common Issues

#### 1. PyBullet Import Error
```
ModuleNotFoundError: No module named 'pybullet'
```
**Solution**: Install PyBullet:
```bash
pip3 install pybullet
```

#### 2. Video Generation Fails
If `trajectory.mp4` generation fails, the script will automatically fall back to GIF format. If both fail, a static image will be saved instead.

**Solution**: Install ffmpeg for MP4 support:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

#### 3. Slow Performance
If planning takes too long:
- Reduce `max_iters`
- Reduce `num_primitives`
- Simplify the environment (fewer obstacles)

#### 4. No Path Found
If the algorithm fails to find a path:
- Increase `max_iters`
- Increase `num_primitives`
- Adjust `goal_eps_pos` and `goal_eps_vel` (make goal region larger)
- Check if the environment is solvable

### Getting Help

If you encounter issues not covered here:
1. Check the console output for error messages
2. Verify all dependencies are installed correctly
3. Ensure Python version is 3.7 or higher
4. Check that PyBullet is working: `python3 -c "import pybullet; print(pybullet.__version__)"`

## License

This project is developed for educational purposes as part of ECE 422 Final Project.

## Acknowledgments

- **PyBullet**: Physics simulation engine
- **RRT Algorithm**: Based on the Rapidly-exploring Random Tree algorithm by LaValle and Kuffner
- **Kinodynamic RRT**: Extension to state space with dynamic constraints

## Contact

For questions or issues related to this project, please refer to the course materials or contact the course instructor.

---

**Last Updated**: December 2024  
**Version**: 1.0  
**Status**: Complete

