#!/bin/bash

# Commands to set up your environment (if any)
# For example, activating a conda environment or setting environment variables
# This is just a placeholder for any setup commands you might need
# echo "Environment setup commands go here"

# Automatically run the notebook
jupyter nbconvert --to notebook --execute --inplace --ClearOutputPreprocessor.enabled=True Onboarding-Tracking.ipynb

# Launch Jupyter notebook with a specific notebook opened by default
jupyter notebook --NotebookApp.default_url='/Onboarding-Tracking.ipynb'