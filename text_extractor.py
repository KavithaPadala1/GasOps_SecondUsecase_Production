# import os
# import base64
# from azure.core.credentials import AzureKeyCredential
# from azure.ai.documentintelligence import DocumentIntelligenceClient
# from azure.ai.documentintelligence.models import AnalyzeResult, AnalyzeDocumentRequest

# # Set your endpoint and key variables with the values from the Azure portal
# endpoint = "document-intelligence-endpoint"
# key = "document-intelligence-key"

# def extract_text_from_pdf(pdf_path):
#     client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    
#     # Read the PDF file and encode it to base64
#     with open(pdf_path, "rb") as f:
#         pdf_data = f.read()
#         base64_data = base64.b64encode(pdf_data).decode('utf-8')
    
#     # Create the analyze request with base64Source
#     analyze_request = AnalyzeDocumentRequest(bytes_source=base64_data)
    
#     poller = client.begin_analyze_document(
#         "prebuilt-read",  # Use prebuilt-read for text extraction
#         analyze_request=analyze_request
#     )
    
#     result: AnalyzeResult = poller.result()
    
#     # Extract text content directly from the result
#     text_content = result.content if result.content else ""
    
#     # Alternative: If you want to extract text line by line
#     if not text_content and result.pages:
#         all_text = []
#         for page in result.pages:
#             if page.lines:
#                 for line in page.lines:
#                     all_text.append(line.content)
#         text_content = "\n".join(all_text)
    
#     # Save to text file
#     # with open(output_txt_path, "w", encoding="utf-8") as out_file:
#     #     out_file.write(text_content)
#     # print(f"Extracted text saved to {output_txt_path}")
    
#     return text_content

# if __name__ == "__main__":
#     extract_text_from_pdf("./temp_extracted_Previous_m.pdf")




import os
import base64
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult

# Set your endpoint and key variables with the values from the Azure portal
endpoint = "document-intelligence-endpoint"  # Replace with your actual endpoint
key = "document-intelligence-key"  # Replace with your actual key

def extract_text_from_pdf(pdf_path):
    client = DocumentIntelligenceClient(endpoint=endpoint, credential=AzureKeyCredential(key))
    
    # Read the PDF file as binary data
    with open(pdf_path, "rb") as f:
        poller = client.begin_analyze_document(
            "prebuilt-read",  # Use prebuilt-read for text extraction
            body=f  # Pass the file object directly as body
        )
    
    result: AnalyzeResult = poller.result()
    
    # Extract text content directly from the result
    text_content = result.content if result.content else ""
    
    # Alternative: If you want to extract text line by line
    if not text_content and result.pages:
        all_text = []
        for page in result.pages:
            if page.lines:
                for line in page.lines:
                    all_text.append(line.content)
        text_content = "\n".join(all_text)
    
    return text_content

if __name__ == "__main__":
    extract_text_from_pdf("./temp_extracted_Previous_m.pdf")
