# Co-Design on Tendon-Driven Gripper  
### By Kiwan Wong

## Project Description
This project focuses on the co-design of a tendon-driven robotic gripper. The goal is to optimize the gripper's performance by balancing functional requirements such as grasping ability, payload, and workspace with cost constraints. The schematic diagram illustrates how design elements like robotic arm selection, material properties, and motor characteristics interact to achieve these goals.

## Key Features
- **Grasping Simulation**: Uses `Env_BallGrasping_V3.py` to generate data for performance analysis.
- **Data Transformation**: Converts CSV files to YAML format using `csv2yaml.py` for compatibility with the MCDP framework.
- **Optimization Framework**: Implements the MCDP framework to solve co-design problems.

## Project Structure
├── Env_BallGrasping_V3.py     # Script for data generation

├── csv2yaml.py                # CSV to YAML file converter

├── FingerModel_V5.py          # Finger modeling utilities

├── solve_query.py             # Query solver using the MCDP framework

├── gripper_system.mcdplib     # MCDP library files for optimization

├── README.md                  # Documentation

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo-url.git
   cd tendon-driven-gripper
2. Install required package
   ```bash
  pip install -r requirements.txt
