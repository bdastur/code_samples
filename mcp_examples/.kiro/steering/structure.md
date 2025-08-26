# Project Structure

## Directory Layout

```
├── .kiro/                    # Kiro IDE configuration and steering rules
├── .vscode/                  # VS Code configuration
├── commonlibs/               # Shared libraries (currently empty)
└── mcp_demo_1/              # Main MCP demonstration module
    ├── mcp_client.py        # MCP client implementation
    ├── mcp_server_calculator.py  # Calculator MCP server
    └── mcpclient.log        # Client execution logs
```

## File Organization

### MCP Server (`mcp_server_calculator.py`)
- Uses FastMCP framework for simplified server implementation
- Implements mathematical operations as MCP tools
- Supports both stdio and HTTP transports
- Uses Click for CLI interface

### MCP Client (`mcp_client.py`)
- Demonstrates MCP client connection patterns
- Integrates with AWS Bedrock for AI model interactions
- Supports both stdio and HTTP transport connections
- Includes comprehensive logging and error handling

## Naming Conventions

- **Files**: Snake case (e.g., `mcp_client.py`, `mcp_server_calculator.py`)
- **Classes**: PascalCase (e.g., `MCPClient`)
- **Functions/Methods**: Snake case (e.g., `process_query`, `chat_loop`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `SYSTEM_INSTRUCTIONS`)

## Code Organization Patterns

- **Single Responsibility**: Each file has a clear, focused purpose
- **Separation of Concerns**: Client and server logic kept separate
- **Modular Design**: Self-contained modules that can be run independently
- **Configuration Centralization**: Settings and constants defined at module level