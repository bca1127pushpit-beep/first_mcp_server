from fastmcp import FastMCP
import random
import json
import os 
import sqlite3
from pydantic import BaseModel,Field


mcp = FastMCP("Simple Calculator Sever")
DB_PATH = os.path.join(os.path.dirname(__file__),"expenses.db")
CATEGORIES_PATH = os.path.join(os.path.dirname(__file__),'categories.json')
def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
           CREATE TABLE IF NOT EXISTS expenses(
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           date TEXT NOT NULL,
           amount REAL NOT NULL,
           category TEXT NOT NULL,
           subcategory TEXT DEFAULT ' ',
           note TEXT DEFAULT ' '
        )
        """)

init_db()
#tool : Expense
# 1 define the pydantic schema for input validation
class ExpenseCreate(BaseModel):
    date:str = Field(description="year-month-date")
    amount:float = Field(gt=0,description="Amount must be greater than zero")
    category:str = Field(min_length=1,strip_whitespace=True)
    subcategory:str = Field(default=" ")
    note:str = Field(default=" ")

@mcp.tool()
def add_expense(expense:ExpenseCreate):
    """Add a new expense entry to the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
                "INSERT INTO expenses(date,amount,category,subcategory,note) VALUES(?,?,?,?,?)",
                (expense.date,expense.amount,expense.category,expense.subcategory,expense.note)
        )
        return{"status":"ok","id":cur.lastrowid}
#list tool expenses
@mcp.tool()
def list_expense(date_start,end_date):
    """Retrieve the expense data from database"""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """
            SELECT id,date,amount,category,subcategory,note
            from expenses
            WHERE date BETWEEN ? AND ? 
            ORDER BY id ASC 
            """,(date_start,end_date)
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]

@mcp.tool()
def summarize(start_date,end_date,category=None):
    """ Summarize expenses bu category within an inclusive date range. """
    with sqlite3.connect(DB_PATH) as c:
        query = ("""
            SELECT category,SUM(amount) AS total_amount
            from expenses
            WHERE date BETWEEN ? AND ? """
        )
        params = [start_date,end_date]
        if category:
            query  += "AND category = ?"
            params.append(category)

        query += "Group BY category ORDER BY category ASC"
        cur  = c.execute(query,params)
        cols = [d[0] for d in cur.fetchall()]
        return [dict(zip(cols,r) for r in cur.fetchall())] 
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