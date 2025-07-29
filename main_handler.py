from intent_router import classify_intent_llm
from sql_query_generator import generate_sql_query, format_results_prompt, generate_sql_with_ai_examples
from query_execution import execute_sql
from azure_client import get_azure_chat_openai
from pdf_extractor import save_pdf_from_binary, save_text_to_file
from text_extractor import extract_text_from_pdf
from ocr_llm import ocr_llm_response


async def handle_user_question(user_question: str, database_name: str = None):
    """
    Main handler: Accepts user question, classifies intent using LLM, routes to SQL-only or SQL+OCR path.
    """
    print(f"User question: {user_question}")
    intent = classify_intent_llm(user_question)
    # If general question, answer directly
    if isinstance(intent, dict) and intent.get("type") == "direct_answer":
        # Return only the answer in the expected FastAPI response format
        return {"intent": "general", "answer": intent["answer"]}

    if intent == "SQL-Only":
        sql = await generate_sql_with_ai_examples(user_question)
        if database_name:
            columns, rows = [], []
            try:
                columns, rows = execute_sql(sql, database_name)
                # Check for BinaryString column for OCR path
                if columns and 'BinaryString' in columns:
                    from ocr_llm import ocr_llm_response
                    # Assume first row, first BinaryString for demo; adjust as needed for your use case
                    binary_index = columns.index('BinaryString')
                    binary_data = rows[0][binary_index] if rows and len(rows[0]) > binary_index else None
                    output_path = f"temp_extracted_{user_question[:10].replace(' ','_')}.pdf"
                    pdf_path = save_pdf_from_binary(binary_data, output_path) if binary_data else None
                    print(f"PDF saved to: {pdf_path}")
                    if pdf_path:
                        text = extract_text_from_pdf(pdf_path)
                        print(f"Extracted text: {text}")
                        if text:
                            text_output_path = output_path.replace('.pdf', '.txt')
                            save_text_to_file(text, text_output_path)
                            print(f"Extracted text saved to: {text_output_path}")
                            # Call OCR LLM and return its answer as the response
                            ocr_answer = ocr_llm_response(user_question, text)
                            print(f"OCR LLM answer: {ocr_answer}")
                            return {"intent": intent, "answer": ocr_answer, "sql": sql}
                            llm_answer = ocr_llm_response(user_question, text)
                            print("OCR LLM answer:", llm_answer)
                azure_chat = None
                try:
                    azure_chat = get_azure_chat_openai()
                except Exception:
                    pass
                prompt = format_results_prompt(columns, rows, user_question, sql)
                llm_response = azure_chat.invoke(prompt) if azure_chat else None
                print(f"LLM response: {llm_response.content}")
                import json
                if not rows or not columns:
                    # If no results, return the LLM's answer (should be an empty array/object)
                    try:
                        return {"intent": intent, "answer": json.loads(llm_response.content) if llm_response else None, "sql": sql}
                    except Exception:
                        return {"intent": intent, "answer": llm_response.content if llm_response else None, "sql": sql}
                # Always return the LLM's JSON answer
                try:
                    return {"intent": intent, "answer": json.loads(llm_response.content) if llm_response else None, "sql": sql}
                except Exception:
                    return {"intent": intent, "answer": llm_response.content if llm_response else None, "sql": sql}
            except Exception as e:
                return {"intent": intent, "error": str(e), "sql": sql}
        return {"intent": intent, "sql": sql}

    # # OCR code need to be implemented
    # elif intent == "SQL+OCR":
    #     sql = generate_sql_query(user_question)
    #     return {"intent": intent, "sql": sql, "ocr": "OCR path to be implemented"}
    # else:
    #     return {"intent": intent, "error": "Unknown intent classification"}
