from fastapi import FastAPI, Header, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
from pydantic import BaseModel
from typing import List, Optional
from sql_query_generator import generate_sql_with_ai_examples, format_results_prompt
from intent_router import classify_intent_llm
from decryption import decode
from query_execution import execute_sql
from azure_client import get_azure_chat_openai
import re
from barcode_api import call_barcode_api

import logging

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Message(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    query: str
    prev_msgs: Optional[List[Message]] = None
    token: Optional[str] = None
    
# Define a request model for barcode lookup
class BarcodeRequest(BaseModel):
    barcode: str


from datetime import datetime
from main_handler import handle_user_question

@app.post("/ask")
async def ask(
    body: AskRequest = Body(...),
    encoded_string: str = Header(...)
):
    query = body.query
    prev_msgs = body.prev_msgs or []
    last_msgs = prev_msgs[-3:]
    context = "\n".join([f"Previous message {i+1} ({msg.role}): {msg.content}" for i, msg in enumerate(last_msgs)])
    full_question = f"{context}\nCurrent question: {query}" if context else query
    print(f"Full question: {full_question}")

    database_name = None
    if encoded_string:
        try:
            decrypted = decode(encoded_string)
            print(f"Decrypted token: {decrypted}")
            database_name = decrypted.get("Database_Name")
        except Exception as e:
            logger.error(f"Failed to decode token: {e}")

    # Pass all relevant info to the orchestration handler
    result = await handle_user_question(full_question, database_name)
    print(f"Printing final result: {result}")



    # Extract the main response text, always as a string
    import json
    response_text = None
    if isinstance(result, dict):
        if "answer" in result:
            response_text = result["answer"]
            # Unwrap nested answer dicts
            while isinstance(response_text, dict) and "answer" in response_text:
                response_text = response_text["answer"]
        elif "error" in result:
            response_text = result["error"]
        elif "sql" in result:
            response_text = result["sql"]
        else:
            response_text = str(result)
    else:
        response_text = str(result)

    # If response_text is not a string (e.g., list or dict), serialize to JSON string
    if not isinstance(response_text, str):
        response_text = json.dumps(response_text, ensure_ascii=False)

    # Build context
    timestamp_bot = datetime.utcnow().isoformat()
    context_list = []
    # Add user message
    context_list.append({
        "role": "user",
        "content": query,
        "timestamp": timestamp_bot
    })
    # Add assistant message
    context_list.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": timestamp_bot
    })

    # User details
    user_details = {
        "session_id": getattr(body, "session_id", None) if hasattr(body, "session_id") else None,
        "token": getattr(body, "token", None) if hasattr(body, "token") else None
    }

    # SQL queries: include the executed SQL if available
    sql_queries = []
    # Try to extract the executed SQL from the result
    if isinstance(result, dict) and "sql" in result and result["sql"]:
        sql_queries.append({
            "db": database_name or "",
            "query": result["sql"]
        })

    return {
        # "response": response_text,
        "answer": response_text,
        "timestamp": timestamp_bot,
        "context": context_list,
        "user_details": user_details,
        "sql_queries": sql_queries
    }


# Endpoint for barcode lookup
@app.post("/barcode")
async def barcode_lookup(
    body: BarcodeRequest,
    encoded_string: str = Header(...),
    token: str = Header(...)
    
    
):
    
    print(f"Received barcode: {token}, body barcode: {body}")
    # rdbase64string = "MIIDPDCCAiSgAwIBAgIQIvJcYfpK2LhDVDZvk0VHCTANBgkqhkiG9w0BAQsFADAgMR4wHAYDVQQDDBVvYW1zYXBpY2xpZW50Y2VydDIwMjMwHhcNMjMwNTA1MTI0NTA2WhcNMjgwNTA1MTI1NTA2WjAgMR4wHAYDVQQDDBVvYW1zYXBpY2xpZW50Y2VydDIwMjMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDCHp/8MJnr+LzRPUsA1tTA3K3vEF/cgBThY1RvY5jLMNFco05diBpwO9SqDoT5N2191RIjgCBSy8AIDYQUOiGxKRwYXGh1RadFyviUh2FKYaumcXHzU1YSLukPvCC5kuBAGGnUAxI7Mye+Pj2sz5MhDQamg5H3S9b5BLDXvU+6rQcf9T2urDp5m5hwyMuBDeG4uzmvvhAiyfG4jghgVib1cNIkTUqxXGAE4m98hXGdeMFfaBa9do/efuYYdIlcv5qDYpM/cTr4+p/v8UxVGJliBDpKFBYKkvhpr1PPtwQfizdRBh1Zcln05TN1tG0QD3VBzXdeTkrvU9WWaTsSP+apAgMBAAGjcjBwMA4GA1UdDwEB/wQEAwIFoDAdBgNVHSUEFjAUBggrBgEFBQcDAgYIKwYBBQUHAwEwIAYDVR0RBBkwF4IVb2Ftc2FwaWNsaWVudGNlcnQyMDIzMB0GA1UdDgQWBBQAPnGEQToIUv3S6cqT8s7pva8CVjANBgkqhkiG9w0BAQsFAAOCAQEAUsVO9IORIaBfYprftvF3AvzzGoGZeClCUxR1bCJafA1h7VAALqCjJ9rsk8YHooyGpE0SoN9NxFaJKtd+SIGo8qhOtDBFXuZg1KGqlMGdp6T9IUFLznG6ODX1Au0S8EBHcFHVlF12r6lNolWRYudqYhnyH9tYwK7N3WyZAwQpD2pKy1L2pBhaZUs4kYzAjpBjiOyWQkjBnz81PqTqA17FXqN8KE18nkrxH/z6JC/OpQGHv39aANS4jqRF4qWbDYIIOYUX7gmw31ChAKeSJaJ2PSxmb/MlCs1CNxHPM/XwAhsFui891+bdtMFkBJhsCHdiAssyAQT1Lz6zrlTHo/vlcA=="
    result = call_barcode_api(body.barcode, token)
    return result

