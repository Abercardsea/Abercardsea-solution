from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy_utils import database_exists, create_database
import sqlparse

'''
This script creates the database and populates it with a skeleton of tables.
Note: the naming convesion is different to Team Hex.
'''

engine = create_engine("sqlite:///database/llanwrydd.db")
if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

with open("database/inifile.sql",'r') as f:
    query = f.read()

sql_queries = sqlparse.split(
    sqlparse.format(query, strip_comments=True)
)

# works!

with engine.connect() as con:
    for query in sql_queries:
        result = con.execute(text(query))
        print(f"{result.rowcount} rows have been updated/selected.")
    con.close()