import re
from barcode_api import call_barcode_api
from azure_client import get_azure_chat_openai
import asyncio

async def barcode_llm(user_question: str, token: str = None):
    pfx_path = "oamsapicert2023.pfx"
    token = "OC85LzIwMjUgNzo0Mzo1MyBQTSYxJkNFREVNT05FVzAzMTQmOC84LzIwMjUgNzo0Mzo1MyBQTSZjZWRlbW8="


    # Extract barcode value from user question using LLM or regex (customize as needed)
    barcode_match = re.search(r'barcode\s*[:=]?\s*([A-Za-z0-9\-]+)', user_question, re.IGNORECASE)
    barcode_value = barcode_match.group(1) if barcode_match else None

    if not barcode_value:
        return "Could not find a barcode value in your question."

    # Call the barcode API using the .pfx file path (recommended for reliability)
    api_result = call_barcode_api(barcode_value, token, pfx_path)
    print(f"API result for barcode {barcode_value}: {api_result}")
    # Prepare prompt for Azure LLM
    azure_chat = get_azure_chat_openai()
    prompt = f"""
You are an expert assistant for barcode lookup and validation.
Here is the data returned from the barcode API:
{api_result}
Summarize the result for the user in a clear, concise way. If there is an error, explain it simply.
User Question:
{user_question}

Answer:
"""
    response = azure_chat.invoke(prompt)
    return response.content.strip()


# rdbase64string = "MIIDPDCCAiSgAwIBAgIQIvJcYfpK2LhDVDZvk0VHCTANBgkqhkiG9w0BAQsFADAgMR4wHAYDVQQDDBVvYW1zYXBpY2xpZW50Y2VydDIwMjMwHhcNMjMwNTA1MTI0NTA2WhcNMjgwNTA1MTI1NTA2WjAgMR4wHAYDVQQDDBVvYW1zYXBpY2xpZW50Y2VydDIwMjMwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDCHp/8MJnr+LzRPUsA1tTA3K3vEF/cgBThY1RvY5jLMNFco05diBpwO9SqDoT5N2191RIjgCBSy8AIDYQUOiGxKRwYXGh1RadFyviUh2FKYaumcXHzU1YSLukPvCC5kuBAGGnUAxI7Mye+Pj2sz5MhDQamg5H3S9b5BLDXvU+6rQcf9T2urDp5m5hwyMuBDeG4uzmvvhAiyfG4jghgVib1cNIkTUqxXGAE4m98hXGdeMFfaBa9do/efuYYdIlcv5qDYpM/cTr4+p/v8UxVGJliBDpKFBYKkvhpr1PPtwQfizdRBh1Zcln05TN1tG0QD3VBzXdeTkrvU9WWaTsSP+apAgMBAAGjcjBwMA4GA1UdDwEB/wQEAwIFoDAdBgNVHSUEFjAUBggrBgEFBQcDAgYIKwYBBQUHAwEwIAYDVR0RBBkwF4IVb2Ftc2FwaWNsaWVudGNlcnQyMDIzMB0GA1UdDgQWBBQAPnGEQToIUv3S6cqT8s7pva8CVjANBgkqhkiG9w0BAQsFAAOCAQEAUsVO9IORIaBfYprftvF3AvzzGoGZeClCUxR1bCJafA1h7VAALqCjJ9rsk8YHooyGpE0SoN9NxFaJKtd+SIGo8qhOtDBFXuZg1KGqlMGdp6T9IUFLznG6ODX1Au0S8EBHcFHVlF12r6lNolWRYudqYhnyH9tYwK7N3WyZAwQpD2pKy1L2pBhaZUs4kYzAjpBjiOyWQkjBnz81PqTqA17FXqN8KE18nkrxH/z6JC/OpQGHv39aANS4jqRF4qWbDYIIOYUX7gmw31ChAKeSJaJ2PSxmb/MlCs1CNxHPM/XwAhsFui891+bdtMFkBJhsCHdiAssyAQT1Lz6zrlTHo/vlcA=="

# token = "{'LoginMasterID': '1', 'Database_Name': 'CEDEMONEW0314', 'OrgID': 'CEDEMO '} "
# print("Barcode LLM module loaded successfully.")
# response =  asyncio.run(barcode_llm("barcode pp5ban2mxh115og0", token, rdbase64string))
# print(f"Response from barcode_llm: {response}")