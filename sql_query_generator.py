# import logging
# import os
# import openai # type: ignore
# import datetime
# from dotenv import load_dotenv
# from azure_client import get_azure_chat_openai
# from abbreviations import ABBREVIATIONS 
# from aisearch.ai_search import cedemo_search

# load_dotenv

# # Initialize Azure OpenAI client
# azure_chat = get_azure_chat_openai()

# # Load OpenAI API key from environment variable
# openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

# SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema", "schema_CEDEMONEW0314.txt")

# def load_schema():
#     with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
#         return f.read()




# def generate_sql_query(user_question, examples=None):
#     """
#     Generate SQL query using Azure OpenAI LLM and schema only.
#     :param user_question: str, the user's natural language question
#     :param examples: str or None, reference examples from AI search
#     :return: str, generated SQL query
#     """
   
#     schema = load_schema()
#     current_year = datetime.datetime.now().year
#     abbreviations_str = "\n".join([f"- {abbr}: {meaning}" for abbr, meaning in ABBREVIATIONS.items()])
#     examples_section = f"\nReference examples from AI search:\n{examples}\n" if examples else ""
    
#     prompt = f"""
# You are an expert in generating accurate Azure SQL queries for transmission work order queries.

# ### Schema:
# Only use these exact table and column names — no spelling changes, no assumptions, no corrections:
# {schema}

# ### Abbreviations:
# You may encounter these abbreviations in user queries. Always expand and interpret them correctly:
# {abbreviations_str}

# Please use the following examples as reference to generate the SQL query:
# {examples_section}

# ## Rules for Generating SQL Queries:
# - Never use any data modifying or altering statements in SQL (such as INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, etc.). Use only SELECT statements.
# - If the user's question is a greeting (such as "hi", "hello", "good morning", etc.), respond ONLY with a friendly greeting message.
# - Use only the tables and columns provided in the following database schema. Do not use or invent any other tables or columns.
# - Do not modify the column names or data in any way.
# - When no date specified use the current year {current_year}.
# - Always include 'WHERE IsActive = 1' for ALL tables that have this column.
# - Always include 'WHERE IsCutout = ''' for ALL tables that have this column.
# - Never display these columns to users: 'WorkActivityFunctionID', 'IsActive', 'IsDeleted'
# - For multi-row subqueries, use IN rather than '='
# - Strictly follow the examples as reference while generating SQL Query.

#  **Transmission Database Specific Rules**:
#         - **Work Order Queries**:
#             - Always join TransmissionWorkOrder with TransmissionISO via TransmissionWorkOrderID
#             - When querying by Work Order Number, use  WorkOrderNo column
#             - When querying by Work Order ID, use TransmissionWorkOrderID column

#         - **Weld/Joint Queries**:
#             - JointID in TransmissionISOMainJoint is the weld number
#             - Always include both heat numbers (SegCompFieldID1 and SegCompFieldID2) when returning weld info
#             - When joining to CompanyMTRFile:
#                 - FIRST try using SegCompField1MTRFileID/SegCompField2MTRFileID
#                 - If those are 0, fallback to SegCompFieldID1/SegCompFieldID2 (heat numbers)

#         - **MTR File Queries**:
#             - When joining CompanyMTRFile to master tables:
#                 - Use AssetCategoryMaster for category descriptions
#                 - Use SizeMaster for size descriptions
#                 - Use MaterialMaster for material descriptions
#                 - Use ManufacturerMaster for manufacturer descriptions


# User Question:
# {user_question}
# SQL:
# """
#     response = azure_chat.invoke(prompt)
#     return response.content.strip()

# # Helper to get examples from ai search 
# async def generate_sql_with_ai_examples(user_question):
#     """
#     Fetches AI search examples for the user question and generates the SQL query using them as reference.
#     """
#     results = cedemo_search(user_question)
#     # Format the results into a string for the prompt
#     examples = "\n\n".join([doc.page_content for doc in results]) if results else None
#     print("ai search examples", examples)
#     return generate_sql_query(user_question, examples=examples)


# def format_results_prompt(columns, rows, user_question, sql_query):
#     """
#     Returns a prompt instructing the LLM to format SQL results as a JSON object with a user-friendly answer and the table.
#     """
#     table_str = (
#         " | ".join(columns) + "\n" +
#         "\n".join(" | ".join(str(cell) for cell in row) for row in rows)
#     )
#     prompt = f"""
# You are an assistant. The user asked: \"{user_question}\"
# The SQL generated was: {sql_query}
# The raw results are:

# {table_str}

# Provide a clear, user-friendly answer to the user's question based on these results.
# Do not add any commentary or extra text.
# """
#     return prompt

# # if __name__ == "__main__":
# #     user_question = "show top 5 rows in ContractorMaster table"
# #     sql = generate_sql_query(user_question)
# #     print("Generated SQL:\n", sql)






#sql_query_generator.py
import os
import openai # type: ignore
import datetime
from dotenv import load_dotenv
from azure_client import get_azure_chat_openai
from abbreviations import ABBREVIATIONS 
from aisearch.ai_search import cedemo_search

load_dotenv

# Initialize Azure OpenAI client
azure_chat = get_azure_chat_openai()

# Load OpenAI API key from environment variable
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")

# Define the path to the schema file
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema", "schema_CEDEMONEW0314.txt")

# Function to load the schema from the file
def load_schema():
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return f.read()



# Function to generate SQL query using Azure OpenAI LLM
def generate_sql_query(user_question, examples=None):
    """
    Generate SQL query using Azure OpenAI LLM and schema only.
    :param user_question: str, the user's natural language question
    :param examples: str or None, reference examples from AI search
    :return: str, generated SQL query
    """

    schema = load_schema()
    current_year = datetime.datetime.now().year
    abbreviations_str = "\n".join([f"- {abbr}: {meaning}" for abbr, meaning in ABBREVIATIONS.items()])
    aisearch_examples = f"\nReference examples from AI search:\n{examples}\n" if examples else ""

    prompt = f"""
You are an expert in generating accurate Azure SQL queries for work order related user questions.

### Schema:
Only use these exact table and column names — no spelling changes, no assumptions, no corrections, no hallucinations:
{schema}

### Abbreviations:
You may encounter these abbreviations in user queries. Always expand and interpret them correctly:
{abbreviations_str}

Please use the following examples as reference to generate the SQL query:
{aisearch_examples}

## Rules for Generating SQL Queries:
- Never use any data modifying or altering statements in SQL (such as INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, etc.). Use only SELECT statements.
- If the user's question is a greeting (such as "hi", "hello", "good morning", etc.), respond ONLY with a friendly greeting message, and do NOT generate any SQL.
- Use only the tables and columns provided in the following database schema. Do not use or invent any other tables or columns.
- Do not modify the column names or data in any way.
- When no date specified use the current year {current_year}.
- Always include 'WHERE IsActive = 1' for ALL tables that have this column.
- Always include 'WHERE IsCutout = ''' for ALL tables that have this column.
- Never display these columns to users: 'WorkActivityFunctionID', 'IsActive', 'IsDeleted'
- Always alias 'JointID' as 'WeldNumber'.
- For multi-row subqueries, use IN rather than '='

    **Transmission Database Specific Rules**:
        - **Work Order Queries**:
            - Always join TransmissionWorkOrder with TransmissionISO via TransmissionWorkOrderID
            - When querying by Work Order Number, use  WorkOrderNo column
            - When querying by Work Order ID, use TransmissionWorkOrderID column

        - **Weld/Joint Queries**:
            - JointID in TransmissionISOMainJoint is the weld number
            - Always include both heat numbers (SegCompFieldID1 and SegCompFieldID2) when returning weld info
            - When joining to CompanyMTRFile:
                - FIRST try using SegCompField1MTRFileID/SegCompField2MTRFileID
                - If those are 0, fallback to SegCompFieldID1/SegCompField2 (heat numbers). Always use 'HeatNumber' as the column name for heat numbers in CompanyMTRFile.
            - For Welds/Weld number queries, always include these columns JointID AS WeldNumber,SegCompFieldID1 AS HeatNumber1,SegCompFieldID2 AS HeatNumber2,SegCompField1MTRFileID,SegCompField2MTRFileID.
            - When the user asks about assets used for a weld number (JointID), do the following:
                - Always include these columns in the SELECT clause:
                    JointID AS WeldNumber,HeatNumber,AssetCategoryDescription AS AssetCategory,SubCategoryDescription AS AssetSubCategory,MaterialDescription AS Material,SizeDescription AS MaterialSize,ManufacturerName AS Manufacturer
                - When returning asset details for both SegCompField1 and SegCompField2:
                    - Use two separate SELECT statements joined with UNION ALL for clarity.
                    - Each SELECT should return the same columns and represent one asset (Asset 1 or Asset 2).
                - When joining to CompanyMTRFile:
                    - Use SegCompField1MTRFileID or SegCompField2MTRFileID when not 0
                    - If the MTRFileID = 0, fallback to matching using:
                        - RTRIM(LTRIM(SegCompFieldID1 or SegCompFieldID2)) IN (SELECT items FROM dbo.Split(cmf.HeatNumber, ';'))
                        - OR cmf.SerialNumber = RTRIM(LTRIM(SegCompFieldID1 or SegCompFieldID2))

        - **MTR File Queries**:
            - When joining CompanyMTRFile to master tables:
                - Use AssetCategoryMaster for category descriptions
                - Use SizeMaster for size descriptions
                - Use MaterialMaster for material descriptions
                - Use ManufacturerMaster for manufacturer descriptions

        - **Chemical/Mechanical Properties Queries**:
            1.When the user asks for chemical or mechanical properties for a heat number or serial number (e.g., "give me mechanical properties for heat no 723260y5"):
                - Always generate a query in the following format (replace the heat number as needed):
                  SELECT top 1 BinaryString
                  FROM CompanyMTRFile
                  WHERE ('<HEAT_NUMBER>' IN (SELECT items FROM dbo.Split(HeatNumber, ';'))
                  OR SerialNumber = '<HEAT_NUMBER>') AND IsActive = 1;
                - Use the provided heat number or serial number from the user question in place of <HEAT_NUMBER>.
                
           2.For user questions about the chemical or mechanical properties of a specific asset:
                - For these kind of questions, always consider the first row of the result set as asset1,next row as asset2, and so on.
                - Next get the HeatNumber or SerialNumber for that asset.
                - Then generate the same SQL query (as in 1), replacing <HEAT_NUMBER> accordingly.

## Output Format:
Your entire response MUST be ONLY the SQL query.
DO NOT include any introductory text, explanations, comments (unless they are part of the SQL query itself, e.g., in a `WITH` clause), or concluding remarks.
DO NOT wrap the SQL in markdown code blocks (```sql ... ```) or any other formatting characters.
Start directly with the SQL query (e.g., 'SELECT' or 'WITH').
End directly with a semicolon.

User Question:
{user_question}
SQL:
"""
    response = azure_chat.invoke(prompt)
    return response.content.strip()

# Helper function to get examples from ai search
async def generate_sql_with_ai_examples(user_question):
    """
    Fetches AI search examples for the user question and generates the SQL query using them as reference.
    """
    results = cedemo_search(user_question)
    # Format the results into a string for the prompt
    examples = "\n\n".join([doc.page_content for doc in results]) if results else None
    print("ai search examples", examples)
    return generate_sql_query(user_question, examples=examples)


# function to format results prompt for LLM
def format_results_prompt(columns, rows, user_question, sql_query):
    """
    Returns a prompt instructing the LLM to format SQL results as a JSON object with a user-friendly answer and the table.
    """
    prompt = f"""
You are an assistant. The user asked: "{user_question}"
The SQL generated was: {sql_query}
The raw results are below.

Columns: {columns}
Rows: {rows}

Return the results as JSON:
- Never truncate, omit, or summarize the results. Always show all rows returned after executing the SQL query, even if there are more than 100 rows.
- If there is only one row, DO NOT return the raw column/value mapping. Instead, generate a clear, user-friendly answer as a string and return it in the following format: {{"answer": "<your answer here>"}}. Do not use the column name as the key.
- If there are multiple rows, return a JSON array of objects, each with column names as keys.
- If there are no results, explain clearly as an answer to that user question, using the same {{"answer": "..."}} format.
- Do not add any commentary or extra text in the JSON response.
- If the results are single row, use clear formatting such as bullet points, lists, or short paragraphs to make the answer easy to read.

Example (multiple rows):
[
  {{"TaskNum": "CE23/24-Hyb", "TaskDesc": "Inspecting the Condition of Exposed Pipe"}},
  {{"TaskNum": "CE31B-Hyb", "TaskDesc": "Installation of Pipe - Installing Pipe in a Ditch"}}
]

Example (single row):
{{"answer": "There are 134 welds in work order 100139423P2."}}

Return only the JSON, nothing else.
"""
    return prompt

# if __name__ == "__main__":
#     user_question = "show top 5 rows in ContractorMaster table"
#     sql = generate_sql_query(user_question)
#     print("Generated SQL:\n", sql)

