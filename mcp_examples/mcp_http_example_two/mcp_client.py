#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import json
import commonlibs.mcp_client_lib as mcp_client_lib



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



def ServerLoggingCallbackHandler(msg: str):
    print("Client: Msg from server: ", msg)


def ServerEllicitationCallbackHandler(msg: str, requestParms: str):
    userInput = input(msg)
    return userInput
    

async def chat_loop(client: mcp_client_lib.MCPClient):
    """Run an interactive chat loop"""
    print("\nMCP Client Started!")
    print("Type your queries or 'quit' to exit.")
    messageHistory = []

    while True:
        try:
            query = input("\nQuery: ").strip()

            if query.lower() == "quit":
                break

            response = await client.processQuery(query=query, systemPrompt=SYSTEM_INSTRUCTIONS, messages=messageHistory)
            print("\n" + response)

        except Exception as e:
            print(f"\nError: {str(e)}")


async def main():
    """Main function to run the MCP client"""

    region = "us-east-1"
    profile = "brd3"
    modelId = "us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    serverUrl = "http://localhost:5001/mcp"
    
    client = mcp_client_lib.MCPClient(region=region, 
                                      profile=profile, 
                                      modelId=modelId,
                                      loggingCallback=ServerLoggingCallbackHandler,
                                      elicitationCallback=ServerEllicitationCallbackHandler)

    try:
        await client.serverConnectStreamableHttp(serverUrl=serverUrl)

        # Available tools
        tools = await client.listToolNames()
        print("Tools available are: ", tools)

        # Start the chat loop
        await chat_loop(client)
    finally:
        print("Finally")
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

