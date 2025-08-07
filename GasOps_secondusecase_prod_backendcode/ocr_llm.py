from azure_client import get_azure_chat_openai

def ocr_llm_response(user_question: str, extracted_text: str):
    """
    Calls the LLM to answer OCR-related user questions using the extracted text from the PDF.
    :param user_question: The user's question (string)
    :param extracted_text: The text extracted from the PDF (string)
    :return: LLM response (string or object)
    """
    prompt = f"""
You are an expert assistant. The following is the extracted text from a document:

---

Please answer the user's question using the below `extracted_text`.
{extracted_text}
---

The user has the following question about this document:
"{user_question}"

Rules:
1. First understand the user's question.
2. If the user question is general, answer directly from your knowledge not from the extracted text like "what is the chemical composition as per API 5L".
3. If the user question requires any comparision or analysis, use the extracted text and your knowledge to provide a detailed answer
   for eg.'For <HeatNumber>, are the chemical properties consistent with API 5L requirements?' then get the extracted text and get the API 5L requirements from your knowledge.And then compare and do the analysis then provide the response to the user.

 
"""
    azure_chat = get_azure_chat_openai()
    response = azure_chat.invoke(prompt)
    return response.content if hasattr(response, 'content') else response
