import azure.functions as func
import logging
import json
import base64
import io
from pypdf import PdfReader

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="decrypt_pdf", methods=["POST"])
def decrypt_pdf(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing PDF decryption request.')

    try:
        # 1. 取得 Request Body
        req_body = req.get_json()
        base64_content = req_body.get('file_content')
        pdf_password = req_body.get('password')

        if not base64_content or not pdf_password:
            return func.HttpResponse("Please pass file_content and password", status_code=400)

        # 2. 解碼 Base64 變回二進位 PDF
        pdf_bytes = base64.b64decode(base64_content)
        pdf_file = io.BytesIO(pdf_bytes)

        # 3. 使用 pypdf 解密
        reader = PdfReader(pdf_file)
        
        if reader.is_encrypted:
            result = reader.decrypt(pdf_password)
            if result == 0:
                return func.HttpResponse("Incorrect password", status_code=401)
        
        # 4. 提取每一頁的文字
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() + "\n"

        # 5. 回傳純文字
        return func.HttpResponse(
            json.dumps({"text": full_text}),
            mimetype="application/json",
            status_code=200
        )

    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)