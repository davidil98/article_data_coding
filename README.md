# Data Analysis for N-GQD Nitrite Sensor

This repository contains the Python scripts and data files used for the analysis and figure generation in the scientific article:

**"A Comparative Study of Synthesis Routes for Nitrogen-Doped Graphene Quantum Dots in Fluorescence Quenching-Based Nitrite Detection"**

Published in *ACS Omega*. (Pending Link)

This work details a comparative study of synthesis routes for nitrogen-doped graphene quantum dots (N-GQDs) and their application in a low-cost, fluorescence-based sensor for nitrite detection.

## Installation

To run these scripts, it is recommended to set up a Python virtual environment.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
    cd your-repository-name
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv
    # Activate on Windows
    venv\Scripts\activate
    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

The main analysis scripts are located in the `scripts/` directory. They can be executed directly from the command line. For example, to generate the calibration curve figures:

```bash
python scripts/plot_calibration_curves.py