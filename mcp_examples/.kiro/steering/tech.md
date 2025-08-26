# Technology Stack

## Core Technologies

- **Python 3.x**: Primary programming language
- **MCP (Model Context Protocol)**: Core framework for AI tool integration
- **FastMCP**: Simplified MCP server implementation framework
- **AWS Bedrock**: AI model hosting and inference service
- **Boto3**: AWS SDK for Python

## Key Dependencies

- `mcp`: Model Context Protocol library
- `fastmcp`: Simplified MCP server framework
- `boto3`: AWS SDK
- `click`: Command-line interface creation
- `pydantic`: Data validation and settings management
- `asyncio`: Asynchronous programming support

## Development Patterns

- **Async/Await**: All MCP operations use asyncio for non-blocking execution
- **Context Managers**: Proper resource cleanup with AsyncExitStack
- **Type Hints**: Full type annotations for better code clarity
- **Pydantic Models**: Field validation and documentation for tool parameters

## Common Commands

```bash
# Run MCP server with stdio transport
python mcp_server_calculator.py start --transport stdio

# Run MCP server with HTTP transport
python mcp_server_calculator.py start --port 5001 --transport streamable-http

# Run MCP client
python mcp_client.py
```

## Configuration

- AWS credentials configured via profiles (default: "brd3")
- Default region: us-east-1
- Default model: Claude 3.5 Sonnet on Bedrock
- Logging configured to write to `mcpclient.log`