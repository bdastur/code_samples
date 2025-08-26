# Model Context Protocol (MCP) Examples

This directory contains examples of Model Context Protocol (MCP) server implementations and client applications. These examples demonstrate how to create and use MCP servers for various use cases, enabling AI models to interact with external tools and data sources.

## Directory Structure

| Directory | Description |
|-----------|-------------|
| commonlibs | Common library files used across multiple examples, including mcp_client_lib.py for MCP client functionality |
| mcp_stdio_example_one | A calculator example demonstrating client-server communication using MCP with stdio transport |

## Examples Directory

| Example Name | Description | Requirements | Tags |
|--------------|-------------|--------------|------|
| mcp_stdio_example_one | A calculator example demonstrating client-server communication using MCP with stdio transport. Includes a server that provides mathematical operations and a client that connects to the server using AWS Bedrock. | Python 3.x, MCP library, AWS Bedrock, boto3 | MCP, Calculator, AWS Bedrock, stdio |

## Getting Started

1. Navigate to the specific example directory you're interested in
2. Install the required dependencies
3. Run the server script first
4. In a separate terminal, run the client script to interact with the server

## Prerequisites

### General Requirements
- Python 3.x
- MCP library
- Click library
- boto3 library

### Common Libraries
- **mcp_client_lib.py**: A reusable client library that provides:
  - MCP server connection (HTTP and stdio)
  - Tool configuration for AWS Bedrock
  - Query processing with LLM integration
  - Direct server tool calling
  - Logging setup

### Example-Specific Requirements
- **mcp_stdio_example_one**: 
  - AWS account with Bedrock access
  - boto3 configured with appropriate credentials
  - AWS Bedrock Claude model access

## Usage Examples

### mcp_stdio_example_one

1. Start the server:
   ```
   python mcp_server_calculator.py start --transport stdio
   ```

2. In a separate terminal, run the client:
   ```
   python mcp_client.py
   ```

3. Enter mathematical queries like:
   - "What is 5 plus 7?"
   - "Calculate 10 minus 3"

## Important Notice

⚠️ **Disclaimer**: These examples are provided as-is for demonstration and learning purposes. They should not be used in production environments without proper review, testing, and modifications to meet your specific requirements and security standards.

## Contributing

Contributions are welcome! Please feel free to submit pull requests with new examples or improvements to existing ones.

## License

Distributed under the Apache 2.0 License. See LICENSE in the root directory for more information.

## Support

For issues and questions, please open a GitHub issue in this repository.
