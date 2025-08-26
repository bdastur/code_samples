# Technology Stack

## Core Technologies

- **Python 3.11+**: Primary programming language
- **AWS SAM (Serverless Application Model)**: Infrastructure as Code and deployment framework
- **AWS Lambda**: Serverless compute platform
- **Docker**: For containerization and local development
- **OpenTelemetry**: Observability framework for metrics transformation

## AWS Services

- **AWS Lambda**: Function execution environment
- **Amazon Kinesis Data Firehose**: Data streaming service
- **Amazon CloudWatch**: Metrics and monitoring
- **Amazon VPC**: Network isolation
- **Network Load Balancer**: Traffic distribution
- **Amazon EC2**: For OpenTelemetry collector hosting

## Development Dependencies

- **requests**: HTTP client library for Python
- **fastmcp**: Fast MCP (Model Context Protocol) server implementation
- **click**: Command-line interface creation toolkit
- **pydantic**: Data validation and settings management

## Build System & Common Commands

### SAM CLI Commands
```bash
# Build the application
sam build --use-container

# Deploy with guided setup
sam deploy --guided

# Deploy with parameters
sam deploy --parameter-overrides subnet1A=<subnet> subnet1B=<subnet> SecurityGroupDefault=<sg> CollectorEndpoint="<endpoint>"

# Local testing
sam local invoke <FunctionName> --event events/event.json
sam local start-api

# View logs
sam logs -n <FunctionName> --stack-name "<stack-name>" --tail

# Cleanup
sam delete --stack-name "<stack-name>"
```

### Testing Commands
```bash
# Install test dependencies
pip install -r tests/requirements.txt --user

# Run unit tests
python -m pytest tests/unit -v

# Run integration tests (requires deployed stack)
AWS_SAM_STACK_NAME="<stack-name>" python -m pytest tests/integration -v
```

### Lambda Layer Setup
```bash
# Setup Python dependencies layer
./setup_layer.sh

# Deploy with custom parameters
./deploy_lambda.sh <subnet1> <subnet2> <security-group> <endpoint>
```

## Runtime Requirements

- Python 3.11 runtime for Lambda functions
- Docker for local development and testing
- AWS CLI configured with appropriate permissions
- SAM CLI installed