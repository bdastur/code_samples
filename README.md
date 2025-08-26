# Cloud Solutions and Code Samples Repository

This repository contains a collection of cloud solutions, code samples, and proof of concepts for various AWS services and integrations. Each solution is contained in its own directory with detailed documentation and implementation guidelines.

## Solutions Directory

| Solution Name | Description | AWS Services | Tags |
|--------------|-------------|--------------|------|
| cloudwatch-streams-transform-lambda | Lambda function that transforms CloudWatch metrics from Kinesis Firehose and forwards them to OpenTelemetry endpoints | AWS Lambda, CloudWatch, Amazon Data Firehose | Observability, Metrics, Integration |
| mcp_examples | Model Context Protocol (MCP) server implementations demonstrating calculator operations and client-server communication patterns | N/A | MCP, Protocol, Development |


## Getting Started

1. Navigate to the specific solution directory you're interested in
2. Read the solution's README.md for detailed implementation instructions
3. Review the architecture diagrams and documentation in the `/docs` folder
4. Explore the source code in the `/src` directory

## Prerequisites

### General Requirements
- AWS Account (for AWS-based solutions)
- Appropriate AWS IAM permissions
- AWS CLI configured

### Solution-Specific Requirements
- **CloudWatch Streams Transform Lambda**: Python 3.11+, SAM CLI, Docker
- **MCP Examples**: Python 3.x, mcp library, click library

Other solution-specific requirements will be listed in each solution's README


## Important Notice

⚠️ **Disclaimer**: The code samples and solutions in this repository are provided as-is for demonstration and learning purposes. These should not be deployed directly to production environments without proper review, testing, and modifications to meet your specific requirements and security standards.

Before implementing any solution:
- Review and understand the code thoroughly
- Test in your own development environment
- Implement appropriate security measures
- Ensure compliance with your organization's standards
- Conduct proper testing and validation

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting pull requests.


## 📜 License

Distributed under the Apache 2.0 License. See LICENSE for more information.



## Support

For issues and questions, please open a GitHub issue in this repository.
