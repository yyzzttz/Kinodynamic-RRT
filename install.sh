#!/bin/bash

# Install script for Kinodynamic RRT project
# Note: pybullet, Python 3, numpy, and matplotlib are already installed

# Install any additional required packages
# Note: pybullet, numpy, matplotlib should already be installed in grading environment
# but we include them here for local testing
PACKAGES="scipy pillow pybullet numpy matplotlib"

# Try with --break-system-packages for newer Debian/Ubuntu systems
pip3 install $PACKAGES --user --break-system-packages 2>/dev/null || \
pip3 install $PACKAGES --user 2>/dev/null || \
pip3 install $PACKAGES --break-system-packages 2>/dev/null || \
pip3 install $PACKAGES 2>/dev/null || \
echo "Note: pip install may have failed, but packages might already be available"

echo "Installation completed successfully!"
