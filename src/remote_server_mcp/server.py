

from fastmcp import FastMCP
from pydantic import BaseModel ,Field
import os
import aiosqlite
import tempfile
import random
import json
import asyncio
TEMP_DIR = tempfile.gettempdir()
DB_PATH = os.path.join(TEMP_DIR,"expenses.db")

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__),"categories.json")
mcp = FastMCP("ExpenseTracker")
async def init_db():
    try:
         async with aiosqlite.connect(DB_PATH) as c:
             await c.execute("""
                CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT ' ',
                note TEXT DEFAULT ' ' 
                )
     """)
             await c.commit() 
    except Exception as e:
        raise RuntimeError(f"Database initialization error:{e}") from e
asyncio.run(init_db())


class ExpenseCreate(BaseModel):
    date:str = Field(description="year-month-date")
    amount:float = Field(gt=0,description="Amount must be greater than zero")
    category:str = Field(min_length=1,strip_whitespace=True)
    subcategory:str = Field(default=" ")
    note:str = Field(default=" ")

@mcp.tool()
async def add_expenses(date,amount,category,subcategory=" ",note=" "):
    """ ADD a new expense entry to the database. """
    try:
         async with aiosqlite.connect(DB_PATH) as c:
                 cur = await c.execute(
                 "INSERT INTO expenses(date,amount,category,subcategory,note) VALUES(?,?,?,?,?)",
                 (date,amount,category,subcategory,note)

             )
                 expense_id = cur.lastrowid
                 await c.commit()
                 return{"status":"ok","id":expense_id,"message":"Expense added successfully"}
    except Exception as e:
        if "readonly" in str(e).lower():
            return {"status":"error","message":f"Database is only readonly mode"}
        return {"status":"error","message":f"Data error:{str(e)}"}
@mcp.tool()
async def list_expenses(start_date,end_date):
    """ RETRIEVE THE EXPENSE DATA  FROM DATABASE """
    try:
         async with aiosqlite.connect(DB_PATH) as c:

             cur = await c.execute(
            """
            SELECT id,date,amount,category,subcategory,note
            FROM expenses
            WHERE date BETWEEN ? AND ? 
            ORDER BY id ASC
            """,
            (start_date,end_date)
        )
             cols = [d[0] for d in cur.description]
             return [dict(zip(cols,r)) for r in cur.fetchall()]
    except Exception as e:
        return {"status":"error","message":f"Error listing expenses:{e}"}

@mcp.tool()
async def summarize(start_date,end_date,category=None):
    """ Summarize expenses by category within an inclusive date range. """
    try:
         async with aiosqlite.connect(DB_PATH) as c:

             query = (
            """
            SELECT category,SUM(amount) AS total_amount
            FROM expenses
            WHERE date BETWEEN ? AND ? 
            """
            
        )
             params = [start_date,end_date]
             if category:
                 query += "AND category = ?"
                 params.append(category)

             query += "GROUP BY category ORDER BY category ASC"
             cur = await c.execute(query,params)
             cols = [d[0] for d in cur.description]
             return [dict(zip(cols,r)) for r in cur.fetchall()]
    except Exception as e:
        return {"status":"error","message":f"Error summarizing expensese{e}"}
       
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