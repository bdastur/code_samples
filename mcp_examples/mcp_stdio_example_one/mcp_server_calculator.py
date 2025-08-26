#!/usr/bin/env python
# -*- coding: utf-8 -*-



"""
MCP Server: Calculator
-----------------------------
The server provides interface for calculating mathematical operations.

Example Usage:
--------------
./calculator.py start --port 5001

"""



import click
import json
import mcp.server
import mcp.server.fastmcp as fastmcp
from typing import List, Dict, Any
from pydantic import Field


mcp = fastmcp.FastMCP()


@mcp.tool(title="add_two_numbers", 
          description="Tool to add two numbers")
def math_operation(ctx: fastmcp.Context,
                   a: float = Field(description="An Float number"), 
                   b: float = Field(description="Second Float number"),
                   operation: str = Field(description="A mathematical operation. Can be add, subtract, multiply, divide")) -> (dict):
    """
    Perform an addition operation for two numbers.

    @params:
      a: number
      b: number

    @returns:
      result. A dictionary of the format {"result": <result>}
    """
    result = {}
    value = 0

    if operation.lower() in ["add", "addition", "sum"]:
        return {"result":  a + b }
    elif operation.lower() in ["sub", "subtract"]:
        return {"result":  a - b }
    else:
        return {"result": "Operation %s Not supported by this tool" % operation}
    


@click.group()
def cli():
    """
    Click cli group
    """
    pass

@cli.command()
@click.option("--port", type=int, help="Server Listener Port", required=True, default=5001)
@click.option("--transport", type=click.Choice(["stdio", "streamable-http"]),
              help="Transport type (sse or streamable-http)", required=True, default="streamable-http")
def start(port, transport):
    """
    Strt MCP Server
    """
    print("MCP Server starting (Transport: %s) on port %d" % (transport, port))
    mcp.settings.port = port
    mcp.run(transport=transport)

def main():
    """
    Main
    """
    cli()

if __name__ == '__main__':
    main()

