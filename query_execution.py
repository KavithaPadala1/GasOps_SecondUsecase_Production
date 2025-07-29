import logging
import os
import pyodbc
from dotenv import load_dotenv
import re

load_dotenv()

SERVER = os.getenv("SERVER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
USERNAME='QuadrantAIUser'

# testing with sql query
# sql_query = """
# SELECT DISTINCT crswf.WorkActivityFunctionID 
# FROM ContractorRouteSheetWorkDescription AS crswd
# JOIN ContractorRouteSheetWorkDescriptiontoWAFMap AS crswf
#   ON crswd.ContractorRouteSheetWorkDescriptionID = crswf.ContractorRouteSheetWorkDescriptionID
# WHERE crswd.WorkDescription LIKE '%Excavate%' AND crswf.IsActive = 1;
# """



def clean_sql(sql):
    # Remove any markdown code block (```sql ... ```) and stray backticks
    sql = re.sub(r"^```sql\s*|^```|```$", "", sql, flags=re.IGNORECASE | re.MULTILINE)
    sql = sql.replace("`", "")
    # Remove everything before the first SELECT or WITH (for CTEs)
    match = re.search(r'(?i)(select|with)\b', sql)
    if match:
        sql = sql[match.start():]
    # Remove any trailing non-SQL explanation/comment after the last semicolon
    if ';' in sql:
        sql = sql[:sql.rfind(';')+1]
    return sql.strip()


def execute_sql(sql_query, database_name):
    """
    Execute the SQL query on the database and return results.
    :param sql_query: str, the SQL query to execute
    :param database_name: str, the database name to use in the connection
    :return: tuple (columns, rows)
    """
    sql_query = clean_sql(sql_query)
    conn_str = (
        # "DRIVER={ODBC Driver 18 for SQL Server};"
        "DRIVER={FreeTDS};" 
        f"SERVER={SERVER},1433;"
        f"DATABASE={database_name};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )
    print(f"Connecting to server: {SERVER} database: {database_name}")
    conn = pyodbc.connect(conn_str)
    try:
        cursor = conn.cursor()
        print(f"Executing SQL: {sql_query}")
        cursor.execute(sql_query)
       
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        # Convert rows to lists for JSON serialization
        rows = [list(row) for row in rows]
        return columns, rows
    finally:
        conn.close()


# if __name__ == "__main__":
#     database_name = "YourDatabaseName"  # Replace with your database name
#     columns, rows = execute_sql(sql_query, database_name)
#     print("Results:")
#     print(columns)
#     for row in rows:
#         print(row)