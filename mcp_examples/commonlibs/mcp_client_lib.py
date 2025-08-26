#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MCP Client Library

This module provides a client implementation for the Model Context Protocol (MCP).
It allows applications to connect to MCP servers, discover available tools,
execute tool calls, and process queries through AWS Bedrock models with tool use capabilities.

The library supports both HTTP streaming and standard I/O communication with MCP servers,
and provides mechanisms for handling server logs and elicitation callbacks.

Dependencies:
    - boto3: For AWS Bedrock API interactions
    - mcp: Core MCP library for client-server communication
"""

#import asyncio
import boto3
import json
import logging
import os
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.types import ElicitResult as MCPElicitResult
from mcp.client.session import ElicitationFnT
from mcp.shared.context import RequestContext
from mcp.types import ElicitRequestParams



#######################################################################
# Setup Logging.
#######################################################################
def get_logger(level=logging.INFO,
               name="Default",
               msg_format:str = '[%(asctime)s %(name)s-%(levelname)s]:  %(message)s',
               date_format: str = '%m-%d %H:%M', 
               output_file_name: str = './mcpclient.log'):
    """
    Configure and return a logger with file and console handlers.
    
    Args:
        level (int): Logging level (default: logging.INFO)
        name (str): Logger name (default: "Default")
        msg_format (str): Format string for log messages
        date_format (str): Format string for timestamps
        output_file_name (str): Path to log file (default: './mcpclient.log')
        
    Returns:
        logging.Logger: Configured logger instance
    """
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




class MCPClient():
    """
    Client implementation for the Model Context Protocol (MCP).
    
    This class provides methods to connect to MCP servers, discover and call tools,
    and process queries through AWS Bedrock models with tool use capabilities.
    """
    
    def __init__(self, region="us-east-1",
                 profile="brd3",
                 modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
                 loggingCallback=None,
                 elicitationCallback=None,
                 verbose=True):
        """
        Initialize MCP Client.
        
        Args:
            region (str): AWS region for Bedrock API (default: "us-east-1")
            profile (str): AWS profile name (default: "brd3")
            modelId (str): Bedrock model ID to use for queries
            loggingCallback (callable, optional): Callback function for server logs
            elicitationCallback (callable, optional): Callback function for handling elicitation requests
            verbose (bool): Enable verbose logging if True (default: True)
        """
        self.modelId = modelId
        self.region = region
        self.profile = profile
        if verbose:
            logLevel = logging.INFO
        else:
            logLevel = logging.WARNING
        
        self.loggingCallback = loggingCallback
        self.elicitationCallback = elicitationCallback

        self.logger = get_logger(name="MCPClient", level=logLevel)
        self.bedrockClient = self.__getBotoBedrockClient()

        # MCP Stream
        self._streamsContext = None
        self._sessionContext = None
        self.session = None
        self.logger.info("MCP Client Initialized!")

    def __getBotoBedrockClient(self):
        """
        Create and return a boto3 client for the Bedrock runtime service.
        
        Returns:
            boto3.client: Configured Bedrock runtime client
        """
        session = boto3.Session(region_name=self.region, profile_name=self.profile)
        client = session.client("bedrock-runtime")
        return client
    
    async def serverLogHandler(self, msg):
        """
        Handle log messages from the MCP server.
        
        This method logs server messages and forwards them to the user-provided
        logging callback if one was specified during initialization.
        
        Args:
            msg: Message object containing log data
        """
        self.logger.info("Server Log: %s" % msg.data)
        if self.loggingCallback:
            self.loggingCallback(msg.data)

    async def serverElicitationCallbackHandler(self, 
                                               requestContext: RequestContext,  
                                               requestParams: ElicitRequestParams):
        """
        Handle elicitation requests from the MCP server.
        
        This method processes requests from the server that require user input.
        If a user-provided elicitation callback was specified during initialization,
        it will be used to handle the request. Otherwise, the method will prompt
        the user directly via the console.
        
        Args:
            requestContext (RequestContext): Context information for the request
            requestParams (ElicitRequestParams): Parameters for the elicitation request
            
        Returns:
            MCPElicitResult: Result of the elicitation with user response and action
        """
        self.logger.info("Server Elicitation callback handler request Context: %s request params: %s" % \
                         (requestContext, requestParams))
        # use the user callback if specified to handle the 
        # Server elicitation
        if self.elicitationCallback:
            userInput = self.elicitationCallback(requestParams.message, requestParams.requestedSchema)
            if userInput.lower() in ["yes", "proceed", "y"]:
                action = "accept"
            else:
                action = "decline"    
            userResponse = {
                "userResponse": userInput
            }
            return MCPElicitResult(action=action,
                               content=userResponse)
        
        userInput = input(requestParams.message)
        userResponse = {
            "userResponse": userInput
        }
        if userInput.lower() in ["yes", "proceed", "y"]:
            action = "accept"
        else:
            action = "decline"

        # TODO: This should call user user callback.
        return MCPElicitResult(action=action,
                               content=userResponse)

    async def serverConnectStreamableHttp(self, serverUrl: str = None,
                                          headers: dict = {}):
        """
        Connect to the MCP Server over Streamable HTTP Transport.
        
        This method establishes a connection to an MCP server using HTTP streaming,
        sets up the client session, and initializes communication.
        
        Args:
            serverUrl (str): URL of the MCP server
            headers (dict): Optional HTTP headers to include in the connection
        """
        self.logger.info("Create streamable http Server connection to %s" % serverUrl)
        self._streamsContext = streamablehttp_client(
            url=serverUrl,
            headers=headers or {},
        )
        read_stream, write_stream, _ = await self._streamsContext.__aenter__()

        self._sessionContext = ClientSession(read_stream,
                                             write_stream,
                                             elicitation_callback=self.serverElicitationCallbackHandler,
                                             logging_callback=self.serverLogHandler)

        self.session: ClientSession = await self._sessionContext.__aenter__()

        await self.session.initialize()

    def serverConnectStdio(serverPath: str, args: str):
        """
        Connect to the MCP Server running locally over STDIO.
        
        This method establishes a connection to a local MCP server using
        standard input/output for communication.
        
        Args:
            serverPath (str): Path to the server executable
            args (str): Command-line arguments to pass to the server
            
        Note:
            This method is currently a placeholder and not implemented.
        """
        pass

    async def listToolNames(self):
        """
        Return the list of tools available to this MCP client.
        
        This method queries the connected MCP server for available tools
        and returns a list of tool objects with name and description.
        
        Returns:
            list: List of dictionaries containing tool names and descriptions
        """
        availableTools = []
        response = await self.session.list_tools()
        for tool in response.tools:
            obj = {}
            obj["name"] = tool.name
            obj["description"] = tool.description
            availableTools.append(obj)
        
        return availableTools

    async def createToolConfig(self) -> str:
        """
        Create a tool configuration for use with Bedrock models.
        
        This method queries the MCP server for available tools and formats them
        into a configuration structure that can be passed to Bedrock models
        to enable tool use capabilities.
        
        Returns:
            dict: Tool configuration dictionary compatible with Bedrock API
        """
        # List tools.
        response = await self.session.list_tools()

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
    
    async def directServerToolCall(self, toolName: str, toolArgs: dict):
        """
        Call a tool provided by the MCP server directly.
        
        This method allows direct invocation of server tools without going through
        an LLM. This can be useful in cases where we know what we want to do and 
        don't need an LLM to provide that information.
        
        Args:
            toolName (str): Name of the tool to call
            toolArgs (dict): Arguments to pass to the tool
            
        Returns:
            dict: Result of the tool execution
        """
        self.logger.info("Invoke Server Tool %s (%s)" % (toolName, toolArgs))
        # Execute tool call.

        result = await self.session.call_tool(toolName, toolArgs)
        resultValue = json.loads(result.content[0].text)
        if resultValue["tool_run_status"] != "success":
            self.logger.error("Tool run status is not successful")
            return {}
        
        return resultValue["result"]

    async def processQuery(self, query: str, systemPrompt: str, messages: str = []) -> str:
        """
        Process a user query using Bedrock with MCP tool integration.
        
        This method sends the user query to a Bedrock model, handles any tool use
        requests from the model by calling the appropriate MCP server tools, and
        returns the final response.
        
        Args:
            query (str): User query to process
            systemPrompt (str): System prompt to provide context to the model
            messages (list): Optional list of previous messages in the conversation
            
        Returns:
            str: Final response text from the model
        """
        stopReason = None

        self.systemPrompt = [
            {
                "text": systemPrompt
            }
        ]
        message = {
            "role": "user",
            "content": [{"text": "%s" % query}]
        }
        messages.append(message)


        toolConfig = await self.createToolConfig()

        while stopReason != "end_turn":
            response = self.bedrockClient.converse(
                modelId=self.modelId,
                messages=messages,
                system=self.systemPrompt,
                toolConfig=toolConfig)

            outputMessage = response["output"]["message"]
            messages.append(outputMessage)

            if response["stopReason"] == "tool_use":
                self.logger.info("LLM request tool use")
                stopReason = "tool_use"
                toolInfo = {}
                content = response["output"]["message"]["content"]
                for contentObj in content:
                    if "toolUse" in contentObj:
                        toolInfo = contentObj["toolUse"]
                        break

                toolName = toolInfo["name"]
                toolArgs = toolInfo["input"]
                toolUseId = toolInfo["toolUseId"]
                self.logger.info("LLM Tool identified: %s (%s)" % (toolName, toolArgs))

                # Execute tool call.
                result = await self.session.call_tool(toolName, toolArgs)
                resultValue = json.loads(result.content[0].text)
                toolResult = {
                    "toolUseId": toolUseId,
                    "content": [{"text": "Result is %s " % (str(resultValue["result"]))}]
                }
                toolResponseMessage = {
                    "role": "user",
                    "content": [
                        {"toolResult": toolResult}
                    ]
                }
                messages.append(toolResponseMessage)
            elif response["stopReason"] == "end_turn":
                stopReason = "end_turn"

                responseText = response["output"]["message"]["content"][0]
                return responseText["text"]

    async def cleanup(self):
        """
        Properly clean up the session and streams.
        
        This method ensures that all resources associated with the MCP client
        session are properly released, including closing the session context
        and stream context.
        """
        if self._sessionContext:
            await self._sessionContext.__aexit__(None, None, None)

        if self._streamsContext:
            await self._streamsContext.__aexit__(None, None, None)
