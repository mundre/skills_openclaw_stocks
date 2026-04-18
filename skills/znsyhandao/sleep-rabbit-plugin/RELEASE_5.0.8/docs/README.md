# Version 5.0.8 - Sleep Rabbit Sleep Health Skill

## Overview

Sleep Rabbit is a professional sleep analysis, stress assessment, and meditation guidance system for OpenClaw. It provides both basic features (working with Python standard library) and advanced features (requiring optional scientific packages).

## Key Features

### Sleep Analysis
- EDF file validation and basic metadata extraction (standard library)
- Full sleep stage analysis with MNE-Python (optional install)
- Sleep quality assessment and recommendations

### Stress Assessment
- Heart rate variability (HRV) calculation
- Stress scoring based on physiological data
- Personalized stress management recommendations

### Meditation Guidance
- Multiple meditation techniques (relaxation, focus, sleep, stress-relief)
- Step-by-step guided meditation instructions
- Duration-based session planning

### File Management
- File system analysis and validation
- Security-conscious file type checking
- Path restriction for safe operation

## Security Features

### Runtime Security (During Skill Execution)
- **100% Local Execution**: No network calls during skill operation
- **No Shell Commands**: Safe execution without [removed [removed].js reference] or [removed [removed].js reference]
- **Path Restriction**: File access limited to skill directory and allowed subdirectories
- **File Type Validation**: Only allowed file types can be processed

### Installation Transparency
- **Basic Features**: Work with Python standard library only, no network required
- **Advanced Features**: Optional installation of MNE, NumPy, SciPy for full EDF analysis
- **Clear Separation**: Users choose between basic (local) and advanced (optional install) modes

### Verification
- **Documentation Consistency**: All security claims verified against code implementation
- **Security Validation**: Built-in security checks in both Python and  components
- **Transparent Design**: Clear declaration of what requires network access vs what runs locally

## Installation

### Method 1: Copy to OpenClaw Skills Directory
```bash
# Copy the skill directory to OpenClaw skills folder
cp -r AISleepGen/ ~/.openclaw/skills/
```

### Method 2: Use OpenClaw Skill Install
```bash
# Install from extracted directory
openclaw skill install ./AISleepGen
```

## Usage

### Basic Commands (Standard Library Only)
- `/file-info <file>`: File system analysis and validation
- `/stress-check <hr-data>`: Stress assessment from heart rate data (comma-separated values)
- `/meditation-guide`: Get personalized meditation guidance
- `/env-check`: Environment diagnostics and dependency checking

### Advanced Commands (Requires Optional Packages)
- `/sleep-analyze <edf-file>`: Full EDF sleep data analysis (requires `pip install mne numpy scipy`)

### Command Examples
```bash
# Basic file validation
/file-info data/sample.edf

# Stress assessment
/stress-check 65,72,68,70,75,69,71

# Meditation guidance (10 minutes, relaxation type)
/meditation-guide 10 relaxation

# Environment check
/env-check
```

## Environment Requirements

### Basic Mode (Out of the Box)
- Python 3.8+
- Standard library only
- File verification and basic analysis
- Heart rate stress assessment
- Meditation guidance

### Advanced Mode (Optional)
- MNE-Python (`pip install mne`)
- NumPy (`pip install numpy`)
- SciPy (`pip install scipy`)
- Full EDF sleep analysis capabilities

## Configuration

The skill uses `config.yaml` for configuration. Key settings include:

- **Security settings**: Path restrictions, file type allowances
- **Plugin configuration**: Enable/disable specific features
- **Output format**: JSON, text, or markdown output
- **Performance limits**: Timeouts, memory limits, worker counts

## Development

### Project Structure
```
AISleepGen/
€ skill.py              # Main Python skill implementation
€ sleep-rabbit-secure[removed [removed] file] # Secure  wrapper
€ config.yaml          # Skill configuration
€ package.json         #  package metadata
€ README.md           # This file
€ SKILL.md            # Detailed skill documentation
€ CHANGELOG.md        # Version history
€ INTEGRATION_GUIDE.md # Integration instructions
€ PLUGIN_USAGE.md     # Plugin usage guide
€ requirements.txt    # Python dependencies (optional)
€ examples/           # Example files
    € sample_config.json
```

### Testing
```bash
# Test the Python skill directly
python skill.py --help

# Test the  wrapper
[removed [removed [removed [removed][removed [removed] file] reference] file] reference] sleep-rabbit-secure[removed [removed] file]

# Run the test script
[removed [removed [removed [removed][removed [removed] file] reference] file] reference] test-plugin[removed [removed] file]
```

## Security Audit

The skill includes built-in security validation:

1. **Code Security**: No network imports, no shell commands
2. **Path Security**: Restricted file system access
3. **Documentation Consistency**: All claims verified against implementation
4. **Installation Transparency**: Clear separation of local vs optional features

Run security audit:
```bash
# From the skill directory
[removed [removed [removed [removed][removed [removed] file] reference] file] reference] sleep-rabbit-secure[removed [removed] file]
```

## Troubleshooting

### Common Issues

1. **"Skill file not found"**: Ensure skill.py is in the correct directory
2. **"MNE not available"**: Install with `pip install mne numpy scipy` for advanced features
3. **"File access denied"**: Check path restrictions in config.yaml
4. **"Invalid file type"**: Only allowed file types can be processed

### Debug Mode
Enable debug logging in config.yaml:
```yaml
logging:
  level: "debug"
```

## Contact Information

- **Author**: Sleep Rabbit Team
- **Email (USA)**: handaocqs103@gmail.com
- **Email (China)**: cqs103@163.com
- **Mobile (China)**: +86 13571924486
- **GitHub**: https://github.com/AISleepGen

## License

MIT License - See LICENSE file for details.

## Changelog

See CHANGELOG.md for version history and changes.

