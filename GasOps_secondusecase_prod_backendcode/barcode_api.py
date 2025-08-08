"""
Call an API using Base64 .pfx client certificate (no password)
Run:
    pip install requests_pkcs12
"""
 
import base64
import requests_pkcs12
 
 


import tempfile
import os

def call_barcode_api(barcode_value, token, pfx_source="oamsapicert2023.pfx"):
    """
    Calls the barcode API using a .pfx client certificate.
    Args:
        barcode_value (str): The barcode to look up.
        token (str): The auth-token value for the API.
        pfx_source (str): Path to the .pfx file or base64 string of the certificate.
    Returns:
        dict: API response as JSON if possible, else raw text or error.
    """
    # token = "OC85LzIwMjUgNzo0Mzo1MyBQTSYxJkNFREVNT05FVzAzMTQmOC84LzIwMjUgNzo0Mzo1MyBQTSZjZWRlbW8="

    url = "https://oamsapi.gasopsiq.com/api/GetData/GetDataUsingBarcodeandValidate"
    params = {"Barcode": barcode_value}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "auth-token": token
    }
    temp_file = None
    try:
        # If the input is a base64 string (not a file path), decode and save as temp file
        if not os.path.isfile(pfx_source):
            try:
                cert_bytes = base64.b64decode(pfx_source)
            except Exception as decode_err:
                return {"error": f"Failed to decode base64 certificate: {decode_err}"}
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pfx")
            temp_file.write(cert_bytes)
            temp_file.close()
            pfx_path = temp_file.name
        else:
            pfx_path = pfx_source
        with open(pfx_path, "rb") as f:
            pfx_data = f.read()
        response = requests_pkcs12.get(
            url,
            headers=headers,
            params=params,
            pkcs12_data=pfx_data,
            pkcs12_password="password1234"
        )
        try:
            result = response.json()
        except Exception:
            result = {"success": True, "data": response.text}
        return result
    except Exception as e:
        return {"error": str(e)}

    finally:
        if temp_file:
            try:
                os.unlink(temp_file.name)
            except Exception:
                pass

# === Example usage for direct script run (matches your original working code style) ===
if __name__ == "__main__":
    # Path to your .pfx file
    pfx_path = "oamsapicert2023.pfx"
    # API Endpoint & Headers
    url = "https://oamsapi.gasopsiq.com/api/GetData/GetDataUsingBarcodeandValidate"
    params = {
        "Barcode": "pp5ban2mxh115og0"
    }
    token = "OC85LzIwMjUgNzo0Mzo1MyBQTSYxJkNFREVNT05FVzAzMTQmOC84LzIwMjUgNzo0Mzo1MyBQTSZjZWRlbW8="
    # Call the function
    result = call_barcode_api(params["Barcode"], token, pfx_path)
    print("API Result:", result)

###########################




# import base64
# import requests_pkcs12

# def call_barcode_api(barcode_value, token, pfx_path="oamsapicert2023.pfx"):
#     """
#     Calls the barcode API using a .pfx client certificate.
#     Args:
#         barcode_value (str): The barcode to look up.
#         token (str): The auth-token value for the API.
#         pfx_path (str): Path to the .pfx file (default: 'oamsapicert2023.pfx').
#     Returns:
#         dict: API response as JSON if possible, else raw text or error.
#     """
#     url = "https://oamsapi.gasopsiq.com/api/GetData/GetDataUsingBarcodeandValidate"
#     params = {
#         "Barcode": barcode_value
#     }
#     headers = {
#         "Accept": "application/json",
#         "Content-Type": "application/json",
#         "auth-token": token
#     }
#     try:
#         with open(pfx_path, "rb") as f:
#             pfx_data = f.read()
#         response = requests_pkcs12.get(
#             url,
#             headers=headers,
#             params=params,
#             pkcs12_data=pfx_data,
#             pkcs12_password="password1234"
#         )
#         try:
#             return response.json()
#         except Exception:
#             return {"success": True, "data": response.text}
#     except Exception as e:
#         return {"error": str(e)}
 