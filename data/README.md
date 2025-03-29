# Ad Generation Data Pipeline

This data pipeline generates ad copy examples using Azure OpenAI for various fields/categories. The generated data can be used for training LLMs or other NLP tasks.

## Overview

The pipeline:
1. Takes a list of fields/categories
2. Generates ad copy examples for each field using Azure OpenAI
3. Processes the fields in batches to avoid rate limits
4. Handles parsing errors and fixes JSON issues
5. Saves results to JSON files

## Directory Structure

```
data/
├── cli.py            # Command-line interface
├── README.md         # This documentation file
├── requirements.txt  # Python dependencies
└── src/              # Source code directory
    ├── __init__.py
    ├── config/       # Configuration settings
    │   ├── __init__.py
    │   ├── fields.json  # JSON file with field definitions
    │   ├── fields.py    # Field groups and definitions
    │   └── settings.py  # Configuration settings
    ├── core/         # Core pipeline functionality
    │   ├── __init__.py
    │   ├── llm.py       # LLM client setup
    │   ├── pipeline.py  # Main pipeline implementation
    │   └── prompts.py   # Prompt templates
    ├── schemas/      # Data models
    │   ├── __init__.py
    │   └── ad_schemas.py # Pydantic models for ads
    └── utils/        # Utility functions
        ├── __init__.py
        ├── file_utils.py # File handling utilities
        └── logging.py    # Logging configuration
```

## Prerequisites

### Installation

Install the required dependencies using pip:

```bash
pip install -r data/requirements.txt
```

The requirements include:
- LangChain and Azure OpenAI SDK for LLM integration
- Pydantic for data validation
- Structlog for structured logging
- Tenacity for retry logic
- Typer for CLI functionality

### API Key Setup (Required)

You **must** set up your Azure OpenAI API key before running the pipeline. The API key is not included in the code for security reasons.

Set up your API key using one of these methods:

1. **Environment variable** (recommended for development):
   ```bash
   export AZURE_OPENAI_API_KEY=your_api_key
   ```

2. **.env file** (recommended for local development):
   Create a `.env` file in the project root:
   ```
   AZURE_OPENAI_API_KEY=your_api_key
   ```

## Usage

### Command-Line Interface

The pipeline provides a comprehensive CLI tool for easy execution:

```bash
# Run with default settings
python -m data.cli

# Run with specific field groups
python -m data.cli --fields demo
python -m data.cli --fields tech
python -m data.cli --fields finance,health

# Customize output location
python -m data.cli --output-dir custom_data

# Control generation parameters
python -m data.cli --batch-size 5 --num-examples 3 --retry-delay 30

# Configure logging
python -m data.cli --log-level DEBUG --no-file-log
```

Run with `--help` to see all available options:

```bash
python -m data.cli --help
```

### Predefined Field Groups

The CLI supports the following predefined field groups:

- `tech`: Technology, Smartphones, Laptops, Software, AI & Machine Learning
- `finance`: Finance, Cryptocurrency, Banking Services, Investment Platforms, Personal Finance
- `health`: Health & Wellness, Fitness Equipment, Mental Health, Yoga & Meditation, Healthcare Services
- `education`: Education & E-Learning, Online Courses, University Programs, Coding Bootcamps, Language Learning
- `entertainment`: Entertainment, Streaming Services, Video Games, Music Streaming, Books & Audiobooks
- `demo`: Technology, Finance, Health & Wellness, Education & E-Learning, Entertainment

### Programmatic Usage

You can also use the pipeline programmatically:

```python
from data.src import main

main(
    fields=["Technology", "Finance"],
    output_dir="output_data",
    batch_size=10,
    num_examples=3,
    retry_delay=30
)
```

## Configuration

You can modify the settings in `src/config/settings.py` to customize the pipeline:

- `azure_openai`: Azure OpenAI API settings
  - `deployment_name`: The deployment name for the Azure OpenAI model
  - `azure_endpoint`: The Azure OpenAI endpoint URL
  - `api_version`: The Azure OpenAI API version
  - `api_key`: The Azure OpenAI API key (should be set via environment variables)
  - `temperature`: The temperature for the LLM generation

- `pipeline`: Data generation pipeline settings
  - `num_examples`: Number of examples to generate per field
  - `batch_size`: Number of fields to process in a batch
  - `output_dir`: Directory for output files
  - `retry_attempts`: Number of retry attempts for failed requests
  - `retry_delay`: Delay between retry attempts in seconds

## Output Format

The final output is a JSON file with the following structure:

```json
[
  {
    "prompt": "User-generated prompt for ad creation",
    "ad_text": "Generated ad text with emojis and markdown"
  },
  ...
]
```

## Adding New Fields

To add new fields, edit the `FIELDS` list in `src/config/fields.py` or modify the `fields.json` file.

## Error Handling

The pipeline includes robust error handling:
- Failed requests are retried with exponential backoff
- Parsing errors are captured and fixed using a separate LLM prompt
- All errors are logged with structured logging

## Logging

The pipeline uses structured logging with the following features:

- **Log Levels**: DEBUG, INFO, WARNING, ERROR levels for different verbosity
- **JSON Logging**: All logs are stored in JSON format for easy parsing
- **Console Output**: Colorized logs in development for better readability
- **File Output**: Daily log files stored in the `logs` directory
- **Contextual Information**: Each log entry includes relevant context data

You can control logging behavior:

```bash
# Set log level via command line
python -m data.cli --log-level=DEBUG

# Configure logging programmatically
from data.src.utils.logging import setup_logging
import logging

setup_logging(log_level=logging.DEBUG, console=True, file=True)
``` 