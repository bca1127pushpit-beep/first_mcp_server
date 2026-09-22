from fastmcp import FastMCP
import random
import json

mcp = FastMCP("Simple Calculator Sever")

# Tool :ADD TWO Numbers

@mcp.tool
def add(a:int,b:int)->float:
    """
    Add two numbers together.

    Args:
    a: First number
    b: Second number
    Returns:
       The Sum of a and b
    """
    return a + b

@mcp.tool
def random_no(min_val:int = 1,max_val:int = 100) ->int:
    """Generate a random number within a range.
    
    Args:
    min_val: Minimum value (default 1)
    max_value: Maximum value (default 100)

    Return:
       A random integer between min_val and max_val

    """    
    return random.randint(min_val,max_val)

@mcp.resource("info://server")
def server_into()->str:
    """Get information about this server."""
    info = {
        "name":"Simple Calculator Server",
        "version":"1.0.0",
        "description":"A basic MCP server with math tools",
        "tools":["add","random_no"],
        "author":"Pushpit"
    }
    return json.dumps(info,indent=2)

if __name__=="__main__":
    mcp.run(transport="http",host="0.0.0.0",port=8000)