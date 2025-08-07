from azure_client import get_azure_chat_openai

azure_chat = get_azure_chat_openai()

def classify_intent_llm(user_question: str) -> str:
    """
    Classifies user intent and optionally returns a direct answer for general questions.
    Returns a dict: {"type": "direct_answer", "answer": ...} for general questions, or a string intent for SQL-related questions.
    """
    """
    Always use the LLM to determine if the question is general (and answer directly) or needs SQL routing, based on the prompt only.
    """
    from datetime import datetime
    now = datetime.now()
    current_date = now.strftime('%B %d, %Y')
    current_year = now.year
    prompt = f"""
You are an expert assistant for work order and pipeline engineering questions.
Today's date is {current_date} and the current year is {current_year}.

Instructions:
- If the user's question is a general question (greetings, what's the date, general engineering, design calculations, standards, formulas, or topics about pipe properties, MAOP, wall thickness, steel grade, ASME codes, etc.), answer it directly and concisely.
- If the user's question is about the weather, and you cannot access real-time weather data, provide a typical or seasonal weather summary for the location and time of year, and mention that you cannot access real-time updates. For example: "I'm unable to access real-time weather updates, but [city] in [month] typically experiences... If you need the latest conditions, check a reliable weather website or app."
- If the question is specifically about database records (such as work order numbers, weld records, asset IDs,chemical /mechanical properties, or requests to look up, list, or retrieve information from the database), do NOT answer, just return: SQL-Only 
User Question:
{user_question}

Answer or Routing intent:
"""
    response = azure_chat.invoke(prompt)
    content = response.content.strip()
    # If LLM returns SQL-Only treat as intent, else as direct answer
    if content in ["SQL-Only"]:
        return content
    return {"type": "direct_answer", "answer": content}
