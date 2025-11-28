#!/bin/bash
# Script to run tests and save timing results with Python version and timestamp

# Get Python version
PYTHON_VERSION=$(uv run python --version | cut -d' ' -f2 | tr -d '\n')
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

# Create results directory if it doesn't exist
RESULTS_DIR="test_results"
mkdir -p "${RESULTS_DIR}"

# Generate output filename
OUTPUT_FILE="${RESULTS_DIR}/${TIMESTAMP}.xml"

# Run tests with timing
echo "Running tests with Python ${PYTHON_VERSION}..."
uv run pytest tests/ --durations=0 --junitxml="${OUTPUT_FILE}"

# Add Python version as a property in the XML
if [ -f "${OUTPUT_FILE}" ]; then
    # Use Python to add the property to the XML
    uv run python -c "
import xml.etree.ElementTree as ET
import sys

tree = ET.parse('${OUTPUT_FILE}')
root = tree.getroot()

# Find or create properties element
properties = root.find('properties')
if properties is None:
    properties = ET.SubElement(root, 'properties')

# Add Python version property
python_prop = ET.SubElement(properties, 'property')
python_prop.set('name', 'python.version')
python_prop.set('value', '${PYTHON_VERSION}')

# Add timestamp property
timestamp_prop = ET.SubElement(properties, 'property')
timestamp_prop.set('name', 'test.run.timestamp')
timestamp_prop.set('value', '${TIMESTAMP}')

tree.write('${OUTPUT_FILE}', encoding='utf-8', xml_declaration=True)
"
fi

# Display results
echo ""
echo "Results saved to: ${OUTPUT_FILE}"
echo "Python version: ${PYTHON_VERSION}"
echo "Total test files in ${RESULTS_DIR}: $(ls -1 ${RESULTS_DIR}/*.xml 2>/dev/null | wc -l | tr -d ' ')"

