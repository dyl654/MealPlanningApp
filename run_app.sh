#!/bin/bash

# Activate the virtual environment
source venv/bin/activate

# Set the PYTHONPATH to the current directory
export PYTHONPATH=$PWD

# Set the DB_FILE environment variable
export DB_FILE=/tmp/tmp.PprCZ40dX8  # Replace with your actual DB file path

# Ensure the directory permissions are correct
sudo chown dylan:dylan /home/dylan/Documents/Recipes/FormattedRecipes
sudo chmod 775 /home/dylan/Documents/Recipes/FormattedRecipes

# Run Uvicorn
python -m uvicorn app:app --reload
 
