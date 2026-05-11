# 📑 Documentation Index

Welcome to the Dataverse Bulk Metadata Update Tool! This index will help you navigate all the documentation.

## 🎯 Start Here

**New users**: Start with **→ [SETUP_GUIDE.md](SETUP_GUIDE.md)** (5 minutes)

## 📚 Documentation Files

### Quick References
| File | Purpose | Time | Level |
|------|---------|------|-------|
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | **Quick start** - Get running in 5 min | 5 min | Beginner ⭐ |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Overview of what was created | 5 min | Beginner |
| [README.md](README.md) | **Complete documentation** | 15 min | All levels 📖 |

### Detailed Guides
| File | Purpose | Time | Level |
|------|---------|------|-------|
| [INSTALLATION.md](INSTALLATION.md) | Setup instructions & troubleshooting | 10 min | Beginner 🛠️ |
| [WORKFLOW.md](WORKFLOW.md) | Step-by-step bulk update workflow | 20 min | Intermediate 🔄 |
| [EXAMPLES.md](EXAMPLES.md) | 10 practical use cases & code examples | 15 min | Advanced 💡 |

## 🔍 Finding What You Need

### "I want to..."

**Get started quickly**
→ [SETUP_GUIDE.md](SETUP_GUIDE.md)

**Understand the complete workflow**
→ [WORKFLOW.md](WORKFLOW.md) → Step 1

**Convert JSON files to CSV**
→ [README.md](README.md) → "JSON to CSV Conversion" section

**Edit metadata in CSV**
→ [WORKFLOW.md](WORKFLOW.md) → Phase 3

**Convert CSV back to JSON**
→ [README.md](README.md) → "CSV to JSON Conversion" section

**Push updates to Dataverse**
→ [README.md](README.md) → "Push Updates to Dataverse" section

**See examples of different use cases**
→ [EXAMPLES.md](EXAMPLES.md)

**Install and configure properly**
→ [INSTALLATION.md](INSTALLATION.md)

**Understand the project structure**
→ [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

**Handle errors**
→ Check "Troubleshooting" in [README.md](README.md)

## 🚀 Quick Command Reference

```bash
# Convert JSON to CSV
python json_to_csv.py --input-dir ./data/json_templates

# Convert CSV to JSON
python csv_to_json.py --csv-file ./data/metadata.csv

# Preview Dataverse changes (dry-run)
python dataverse_api.py --csv-file ./data/metadata.csv

# Apply Dataverse changes
python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run
```

## 📂 Project Files

### Python Scripts
- `utils.py` - Utility functions
- `json_to_csv.py` - JSON to CSV converter
- `csv_to_json.py` - CSV to JSON converter
- `dataverse_api.py` - Dataverse API interface

### Data Files
- `data/json_templates/` - Your JSON template files
- `data/json_output/` - Generated JSON files
- `data/metadata.csv` - Editable metadata file

### Configuration
- `config.ini` - Configuration file
- `requirements.txt` - Python dependencies
- `.gitignore` - Git ignore rules

### Utilities
- `quick_start.sh` - Automated quick start script

## 🎓 Learning Paths

### Path 1: Quickest Start (5 minutes)
1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Place JSON files in `data/json_templates/`
3. Run `python json_to_csv.py`
4. Start editing CSV

### Path 2: Complete Understanding (1 hour)
1. Read [SETUP_GUIDE.md](SETUP_GUIDE.md) (5 min)
2. Read [README.md](README.md) (15 min)
3. Follow [WORKFLOW.md](WORKFLOW.md) (20 min)
4. Review [EXAMPLES.md](EXAMPLES.md) (20 min)

### Path 3: Developer/Advanced (2 hours)
1. Complete Path 2
2. Study individual Python modules
3. Review [EXAMPLES.md](EXAMPLES.md) custom scripts
4. Create your own customizations

## 🆘 Troubleshooting

**Installation Issues**
→ [INSTALLATION.md](INSTALLATION.md) → "Troubleshooting Installation"

**Workflow Issues**
→ [WORKFLOW.md](WORKFLOW.md) → "Troubleshooting During Workflow"

**General Issues**
→ [README.md](README.md) → "Troubleshooting" section

**API/Dataverse Issues**
→ [README.md](README.md) → "Troubleshooting" or [EXAMPLES.md](EXAMPLES.md)

## 💾 File Structure Overview

```
.
├── 📄 Documentation
│   ├── README.md                    # Main documentation
│   ├── SETUP_GUIDE.md               # Quick start
│   ├── INSTALLATION.md              # Installation help
│   ├── WORKFLOW.md                  # Step-by-step workflow
│   ├── EXAMPLES.md                  # Use cases & examples
│   ├── PROJECT_SUMMARY.md           # Project overview
│   └── INDEX.md                     # This file
│
├── 🐍 Python Code
│   ├── utils.py                     # Utilities
│   ├── json_to_csv.py               # JSON → CSV
│   ├── csv_to_json.py               # CSV → JSON
│   └── dataverse_api.py             # Dataverse API
│
├── 📊 Data
│   ├── data/json_templates/         # Input JSON files
│   ├── data/json_output/            # Output JSON files
│   └── data/metadata.csv            # CSV for editing
│
├── ⚙️ Configuration
│   ├── config.ini                   # Settings
│   ├── requirements.txt             # Dependencies
│   ├── .gitignore                   # Git ignore
│   └── LICENSE                      # License
│
└── 🚀 Utilities
    └── quick_start.sh               # Quick start script
```

## 🔑 Key Concepts

### DOI (Digital Object Identifier)
- Unique identifier for your dataset
- Format: `doi:10.5061/dryad.example`
- First column in CSV

### Dataset Name
- Human-readable name
- Second column in CSV
- Used as reference only

### File Metadata
- Individual file information
- Description, path, type, size
- Editable in CSV format

### Status Tracking
- Track what was updated
- Values: pending, updated, no_changes, skipped
- Helps audit changes

## 📞 Getting Help

1. **Check documentation**: Most questions answered in docs
2. **Review examples**: [EXAMPLES.md](EXAMPLES.md) has 10 use cases
3. **Check troubleshooting**: Each doc has troubleshooting section
4. **Review logs**: Check `logs/` directory for error messages

## ✅ Before You Start

- [ ] I've read SETUP_GUIDE.md
- [ ] I have Python 3.7+ installed
- [ ] I have JSON files ready
- [ ] I understand the workflow basic (JSON → CSV → JSON → Dataverse)
- [ ] I have my Dataverse API token (if using API)

## 🎉 You're Ready!

Start with [SETUP_GUIDE.md](SETUP_GUIDE.md) and you'll be updating metadata in minutes!

---

**Last Updated**: May 2026  
**Python**: 3.7+  
**License**: MIT
