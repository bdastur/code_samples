# MCP HTTP Example Two

This example demonstrates the implementation of a Model Context Protocol (MCP) client and server using HTTP transport. The example showcases a calculator service that can perform mathematical operations through MCP tools.

## Key Capabilities Demonstrated

### 1. HTTP Transport

This example demonstrates communication between MCP client and server using HTTP streaming transport:

- The server is configured to use `streamable-http` transport on port 5001
- The client connects to the server using the `serverConnectStreamableHttp` method
- HTTP transport allows the MCP server to be hosted on a different machine than the client
- The transport layer handles bidirectional communication between client and server

Example server configuration:
```python
mcp.settings.port = 5001
mcp.run(transport="streamable-http")
```

Example client connection:
```python
await client.serverConnectStreamableHttp(serverUrl="http://localhost:5001/mcp")
```

### 2. Server Logging

The example demonstrates server-side logging capabilities:

- The server can send log messages to the client using the `ctx.info()` method
- The client receives these logs through a callback mechanism (`ServerLoggingCallbackHandler`)
- Logs are displayed to the client console and can be used for debugging or monitoring
- This provides visibility into server-side operations from the client perspective

Example server logging:
```python
await ctx.info("[calculator-math_operation] started (%f, %f, %s)" % (a, b, operation))
```

Example client log handler:
```python
def ServerLoggingCallbackHandler(msg: str):
    print("Client: Msg from server: ", msg)
```

### 3. Server Elicitation

The example implements server elicitation capabilities:

- The client provides an elicitation callback (`ServerEllicitationCallbackHandler`)
- This allows the server to request input from the user during tool execution
- The user's response is sent back to the server to continue processing
- Elicitation enables interactive workflows where the server can prompt for additional information

Example client elicitation handler:
```python
def ServerEllicitationCallbackHandler(msg: str, requestParms: str):
    userInput = input(msg)
    return userInput
```

## Running the Example

### Starting the Server

1. Navigate to the example directory:
   ```
   cd mcp_examples/mcp_http_example_two
   ```

2. Start the server:
   ```
   python mcp_server_calculator.py start --port 5001 --transport streamable-http
   ```

### Running the Client

1. In a separate terminal, navigate to the example directory:
   ```
   cd mcp_examples/mcp_http_example_two
   ```

2. Run the client:
   ```
   python mcp_client.py
   ```

3. Enter mathematical queries when prompted, for example:
   - "What is 5 plus 7?"
   - "Calculate 10 multiplied by 3"
   - "Subtract 15 from 30"

## Implementation Details

- The server implements a calculator tool that supports addition, subtraction, and multiplication operations
- The client uses AWS Bedrock with Claude to interpret user queries and call the appropriate server tools
- The client maintains a conversation history to provide context for follow-up questions
- The server can be extended with additional tools by adding more decorated functions
