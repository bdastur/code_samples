# Project Structure

## Repository Organization

```
├── README.md                           # Main repository documentation
├── LICENSE                            # Apache 2.0 license
├── .gitignore                         # Git ignore patterns
├── cloudwatch-streams-transform-lambda/  # Primary solution directory
│   ├── README.md                      # Solution-specific documentation
│   ├── docs/                          # Architecture diagrams and documentation
│   │   ├── cwmetrics_streaming.drawio # Architecture diagram source
│   │   └── cwmetrics_streaming.drawio.png # Architecture diagram image
│   └── sam_helper/                    # SAM application directory
│       └── lambda-firehose-transform/ # Lambda function implementation
│           ├── template.yaml          # SAM template (IaC)
│           ├── samconfig.toml         # SAM configuration
│           ├── code/                  # Lambda function source code
│           │   ├── app.py            # Main Lambda handler
│           │   └── requirements.txt   # Python dependencies
│           ├── layer/                 # Lambda layer dependencies
│           │   ├── requirements.txt   # Layer dependencies
│           │   └── python/           # Installed Python packages
│           ├── events/               # Test event data
│           │   └── event.json        # Sample Firehose event
│           ├── tests/                # Test suite
│           │   ├── unit/             # Unit tests
│           │   └── requirements.txt   # Test dependencies
│           ├── deploy_lambda.sh      # Deployment script
│           └── setup_layer.sh        # Layer setup script
└── mcp_examples/                      # MCP server examples
    └── mcp_demo_1/                   # Calculator MCP server demo
        ├── mcp_server_calculator.py  # MCP server implementation
        └── mcp_client.py            # MCP client example
```

## Directory Conventions

### Solution Structure
- Each major solution has its own top-level directory
- Solutions include comprehensive README.md with setup instructions
- Architecture diagrams stored in `docs/` subdirectory
- Use descriptive, kebab-case naming for solution directories

### SAM Application Layout
- `template.yaml`: AWS SAM template defining infrastructure
- `samconfig.toml`: SAM CLI configuration file
- `code/`: Lambda function source code directory
- `layer/`: Lambda layer dependencies and setup
- `events/`: Test event JSON files for local testing
- `tests/`: Comprehensive test suite with unit and integration tests

### Python Code Organization
- Main Lambda handler in `app.py`
- Use descriptive function names following snake_case convention
- Include comprehensive docstrings for all functions
- Separate concerns: transformation logic, API calls, error handling

### Configuration Management
- Environment variables for runtime configuration (endpoints, etc.)
- SAM parameters for deployment-time configuration
- Shell scripts for common deployment tasks with parameter validation

### Testing Structure
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Separate requirements.txt for test dependencies
- Use pytest framework for all testing

## File Naming Conventions

- Use snake_case for Python files and functions
- Use kebab-case for directories and shell scripts
- Use descriptive names that indicate purpose
- Include file extensions in documentation references