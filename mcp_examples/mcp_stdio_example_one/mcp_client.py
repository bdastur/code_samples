#!/usr/bin/env python
# -*- coding: utf-8 -*-


import asyncio
import boto3
import json
import logging
from typing import Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client
from strands.tools.mcp.mcp_client import MCPClient


#######################################################################
# Setup Logging.
#######################################################################
def get_logger(level=logging.INFO,
               name="Default",
               msg_format:str = '[%(asctime)s %(name)s-%(levelname)s]:  %(message)s',
               date_format: str = '%m-%d %H:%M', 
               output_file_name: str = './mcpclient.log'):

    print("Get Logger: %s" % name)
    logger = logging.getLogger(name)

    logging.basicConfig(level=level,
                        format=msg_format,
                        datefmt=date_format,
                        filename=output_file_name,
                        filemode='w')

    if logger.hasHandlers():
        logger.handlers.clear()

    # Set console message format. Can be the same.
    consoleMsgFormat:str = msg_format

    console = logging.StreamHandler()
    #avoid logs below INFO serity to standard out
    console.setLevel(logging.ERROR)
    console.setFormatter(logging.Formatter(consoleMsgFormat))
    # add the handler to the root logger
    logger.addHandler(console)

    return logger



SYSTEM_INSTRUCTIONS = """
[purpose] You are a calculator agent. You will use the tools that are available to you to answer questions
specific to math calculations. You should expect results in dictionary/json format.[/purpose]
[instructions]
1. Only answer questions that involve math calculations.
2. Only use tools that are available.
3. The tools return value will always be a dictionary. 
3. If you don't find a specific tool for the operation respond with "I cannot help you with this"
4. Return the output in a simple text format. Example "The sum of 4 and 5 I calculated is 9"
"""


class MCPClient():
    def __init__(self, 
                 region="us-east-1", 
                 profile="brd3", 
                 modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0"):
        self.logger = get_logger(name="McpClient", level=logging.INFO)
        self.modelId = modelId
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        botoSession = boto3.Session(region_name=region, profile_name=profile)
        self.bedrockClient = botoSession.client("bedrock-runtime")

    async def serverConnectStdio(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path, "start", "--transport", "stdio"],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def serverConnectStreamableHttp(self, serverUrl, headers: Optional[dict] = None):
        """
        Connect to an MCP Server running with HTTP streamable transport.
        """
        self._streams_context = streamablehttp_client(
            url=serverUrl,
            headers=headers or {},
        )
        read_stream, write_stream, _ = await self._streams_context.__aenter__()

        self._session_context = ClientSession(read_stream, write_stream)
        self.session: ClientSession = await self._session_context.__aenter__()

        await self.session.initialize()

        #response = await self.session.list_tools()
        #print("Response from list tools: esponse is: ", response, response.tools)

    async def createToolConfig(self) -> str:
        # List tools.
        response = await self.session.list_tools()
        self.logger.info("create tool config response: %s" % response)

        # Get available tools.
        toolConfig = {
            "tools": []
        }
        for tool in response.tools:
            obj = {"toolSpec": {}}
            obj["toolSpec"]["name"] = tool.name
            obj["toolSpec"]["description"] = tool.description
            obj["toolSpec"]["inputSchema"] = {
                "json": {
                    "type": "object",
                    "properties": {}
                }
            }
            # Todo: the properties. description can be better populated.
            # Currently it is not getting populated.
            for property in tool.inputSchema["properties"]:
                propObj = tool.inputSchema["properties"][property]
                obj["toolSpec"]["inputSchema"]["json"]["properties"][property] = {
                    "type": propObj["type"],
                    "description": propObj["title"]
                }

            toolConfig["tools"].append(obj)

        return toolConfig

    async def process_query(self, query: str) -> str:
        """Process the query"""
        toolConfig = await self.createToolConfig()

        # import pprint
        # pp = pprint.PrettyPrinter()
        # pp.pprint(toolConfig)

        # Call the bedrock converse API to perform operations.
        messages = [{
                "role": "user",
                "content": [{"text": "%s" % query}]
            }]

        self.systemPrompt = [
            {
                "text": SYSTEM_INSTRUCTIONS 
            }
        ]

        response = self.bedrockClient.converse(
                modelId=self.modelId,
                messages=messages,
                system=self.systemPrompt,
                toolConfig=toolConfig)


        outputMessage = response["output"]["message"]
        messages.append(outputMessage)

        if response["stopReason"] == "tool_use":
            toolInfo = {}
            content = response["output"]["message"]["content"]
            for contentObj in content:
                if "toolUse" in contentObj:
                    toolInfo = contentObj["toolUse"]
                    break

            toolName = toolInfo["name"]
            toolArgs = toolInfo["input"]

            # Execute tool call.
            result = await self.session.call_tool(toolName, toolArgs)

            resultValue = json.loads(result.content[0].text)
            toolResult = {
                "toolUseId": toolInfo["toolUseId"],
                "content": [{"text": "Result is %s " % (str(resultValue["result"]))}]
            }

            toolResponseMessage = {
                "role": "user",
                "content": [
                    {"toolResult": toolResult}
                ]
            }
            messages.append(toolResponseMessage)

            response = self.bedrockClient.converse(
                modelId=self.modelId,
                messages=messages,
                toolConfig=toolConfig)

            responseText = response["output"]["message"]["content"][0]
            return responseText["text"]

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self.session:
            await self.session.__aexit__(None, None, None)

       
    


async def main():
    """Main function to run the MCP client"""

    region = "us-east-1"
    profile = "brd3"
    serverUrl = "http://localhost:5001/mcp"
    

    client = MCPClient(region, profile)

    try:
        #await client.serverConnectStreamableHttp(serverUrl)
        await client.serverConnectStdio(server_script_path="./mcp_server_calculator.py")
        # Start the chat loop
        await client.chat_loop()
    finally:
        print("Finally")
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
