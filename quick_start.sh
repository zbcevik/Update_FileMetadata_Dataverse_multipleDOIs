#!/bin/bash
# Quick start script for bulk updates
# Usage: ./quick_start.sh

set -e

echo "==================================================="
echo "Dataverse Bulk Metadata Update - Quick Start"
echo "==================================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet requests

# Create directories
echo "Creating data directories..."
mkdir -p data/json_templates data/json_output backups logs

# Check for sample JSON files
if [ ! -f "data/json_templates/climate_data_2024.json" ]; then
    echo "Note: No JSON files found in data/json_templates/"
    echo "Please add your JSON files before proceeding"
    echo ""
fi

# Convert JSON to CSV
echo ""
echo "Step 1: Converting JSON to CSV..."
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/metadata.csv

echo ""
echo "✓ CSV created: data/metadata.csv"
echo ""
echo "Next steps:"
echo "1. Edit data/metadata.csv with new descriptions"
echo "2. Run: python csv_to_json.py --csv-file ./data/metadata.csv"
echo "3. Run: python dataverse_api.py --csv-file ./data/metadata.csv"
echo ""
echo "See WORKFLOW.md for detailed instructions"
