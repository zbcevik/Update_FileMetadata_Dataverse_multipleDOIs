# Installation and Setup Guide

This guide provides detailed instructions for setting up the Dataverse Bulk Metadata Update Tool.

## System Requirements

- **Python**: 3.7 or higher
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: ~200MB for dependencies
- **Internet**: For Dataverse API access

## Installation Steps

### 1. Clone or Download the Repository

```bash
# Option A: Clone with Git
git clone https://github.com/your-org/Update_FileMetadata_Dataverse_multipleDOIs.git
cd Update_FileMetadata_Dataverse_multipleDOIs

# Option B: Download ZIP
# Download from GitHub and extract
unzip Update_FileMetadata_Dataverse_multipleDOIs.zip
cd Update_FileMetadata_Dataverse_multipleDOIs
```

### 2. Create Virtual Environment (Recommended)

Creating a virtual environment isolates project dependencies:

**On macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

**On Windows:**
```bash
# Create virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### 3. Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install required packages
pip install requests

# Verify installation
python -c "import requests; print(f'requests version: {requests.__version__}')"
```

### 4. Verify Installation

```bash
# Test Python version
python --version
# Should show: Python 3.7.x or higher

# Test imports
python -c "from utils import load_json_file; print('✓ Utils module loaded')"

# Test script availability
python json_to_csv.py --help
python csv_to_json.py --help
python dataverse_api.py --help
```

## Directory Structure Setup

After installation, you should have:

```
Update_FileMetadata_Dataverse_multipleDOIs/
├── utils.py
├── json_to_csv.py
├── csv_to_json.py
├── dataverse_api.py
├── config.ini
├── README.md
├── WORKFLOW.md
├── INSTALLATION.md (this file)
├── data/
│   ├── json_templates/          # Your JSON files go here
│   ├── json_output/             # Generated JSON files
│   └── metadata.csv             # CSV for editing
├── backups/                      # Automatic backups
├── logs/                         # Operation logs
└── venv/                         # Virtual environment (if created)
```

Create the necessary directories:

```bash
# Create data directories if they don't exist
mkdir -p data/json_templates data/json_output
mkdir -p backups logs

# Verify
ls -la data/
# Should show: json_templates, json_output, metadata.csv
```

## Configuration

### 1. Basic Configuration

Edit `config.ini` with your settings:

```ini
[dataverse]
server_url = https://your-dataverse-instance.org
api_token = ${DATAVERSE_API_TOKEN}
```

### 2. Environment Variables (Secure)

Instead of hardcoding credentials, use environment variables:

**On macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export DATAVERSE_SERVER_URL="https://your-dataverse.org"
export DATAVERSE_API_TOKEN="your-secret-token"

# Apply changes
source ~/.bashrc  # or ~/.zshrc
```

**On Windows (Command Prompt):**
```cmd
setx DATAVERSE_SERVER_URL "https://your-dataverse.org"
setx DATAVERSE_API_TOKEN "your-secret-token"

# Restart Command Prompt for changes to take effect
```

**On Windows (PowerShell):**
```powershell
$env:DATAVERSE_SERVER_URL = "https://your-dataverse.org"
$env:DATAVERSE_API_TOKEN = "your-secret-token"

# To make permanent, use:
[Environment]::SetEnvironmentVariable("DATAVERSE_SERVER_URL", "your-value", "User")
```

### 3. Verify Configuration

```bash
# Check environment variables are set
echo $DATAVERSE_SERVER_URL
echo $DATAVERSE_API_TOKEN

# Test connection
python dataverse_api.py --help
```

## Getting Dataverse API Token

1. **Go to your Dataverse instance**
   - Navigate to: https://your-dataverse.org

2. **Log in to your account**
   - Click on your profile icon (top right)
   - Select "Account"

3. **Generate API Token**
   - Look for "Create API Token" button
   - Click to generate
   - Copy the token immediately and save securely

4. **Store securely**
   - Never commit to version control
   - Use environment variables only
   - Treat like a password

## Troubleshooting Installation

### Issue: "Python command not found"

**Solution:**
```bash
# Check if Python is installed
which python3
# or
python --version

# If not installed:
# macOS: brew install python3
# Linux: sudo apt-get install python3
# Windows: Download from python.org
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install --upgrade pip
pip install requests

# Verify
pip list
```

### Issue: Permission denied errors

**Solution:**
```bash
# On macOS/Linux, use sudo (not recommended, but sometimes needed)
sudo pip install requests

# Better: Fix permissions
sudo chown -R $USER /usr/local/lib/python3.x/site-packages/

# Or use the --user flag
pip install --user requests
```

### Issue: "requests" module not found

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Install requests
pip install requests

# Verify it's installed
python -c "import requests; print('OK')"
```

## First Run Checklist

After installation, verify everything works:

- [ ] Python 3.7+ installed: `python --version`
- [ ] Virtual environment created: `ls -la venv/`
- [ ] Virtual environment activated: `(venv)` shows in prompt
- [ ] Dependencies installed: `pip list | grep requests`
- [ ] Directories created: `ls -la data/`
- [ ] Test scripts run: `python json_to_csv.py --help`
- [ ] Sample data exists: `ls -la data/json_templates/`
- [ ] Dataverse server accessible: `curl -s https://your-dataverse.org/api/v1/info/version`

## Quick Test

Run a quick test to verify everything:

```bash
# 1. Activate environment
source venv/bin/activate

# 2. Convert JSON to CSV
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/test_metadata.csv

# 3. Check output
head data/test_metadata.csv

# 4. Convert back to JSON
python csv_to_json.py \
    --csv-file ./data/test_metadata.csv \
    --output-dir ./data/test_json_output

# 5. Verify output
ls -la data/test_json_output/
cat data/test_json_output/doi_*.json | python -m json.tool | head -20
```

Expected output:
```
✓ Successfully converted X rows to ./data/test_metadata.csv
✓ Created: ./data/test_json_output/doi_*.json
✓ Successfully converted X JSON files to ./data/test_json_output
```

## Docker Installation (Optional)

For containerized deployment:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir requests

# Create necessary directories
RUN mkdir -p data/json_templates data/json_output backups logs

CMD ["/bin/bash"]
```

Build and run:

```bash
# Build image
docker build -t dataverse-bulk-update .

# Run container
docker run -it -v $(pwd)/data:/app/data dataverse-bulk-update

# Inside container
python json_to_csv.py --help
```

## Development Setup (Optional)

For contributing or development:

```bash
# Install additional development dependencies
pip install pytest pytest-cov black flake8

# Run tests
pytest

# Format code
black .

# Check code style
flake8 .
```

## Updating Installation

```bash
# Update all packages
pip install --upgrade pip

# Reinstall dependencies
pip install --upgrade requests

# Check for outdated packages
pip list --outdated
```

## Uninstalling

```bash
# Remove virtual environment
rm -rf venv/

# Remove the entire project directory
rm -rf Update_FileMetadata_Dataverse_multipleDOIs/
```

## Next Steps

After successful installation:

1. **Read the README**: `cat README.md`
2. **Review WORKFLOW.md**: `cat WORKFLOW.md`
3. **Place JSON files**: Put your JSON templates in `data/json_templates/`
4. **Test conversion**: Run `python json_to_csv.py --help`
5. **Set up credentials**: Add Dataverse API token to environment variables
6. **Run first conversion**: Follow the Quick Start guide in README.md

## Support

For issues:

1. Check that Python version is 3.7+
2. Verify virtual environment is activated
3. Ensure `requests` is installed: `pip install requests`
4. Check environment variables are set: `echo $DATAVERSE_API_TOKEN`
5. Verify JSON files are in correct location
6. Review error messages in `logs/` directory

## Additional Resources

- Python Documentation: https://docs.python.org/3/
- Requests Library: https://docs.requests.org/
- Dataverse API Docs: https://guides.dataverse.org/en/latest/api/

