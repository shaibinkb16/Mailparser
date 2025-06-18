from flask import Flask, request, jsonify
from llm_utils import extract_invoice_data
from config import Config
import logging
import json

app = Flask(__name__)

logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle Mailparser webhook requests"""
    try:
        logger.info("Received webhook request")
        
        payload = request.json
        if not payload:
            logger.warning("Empty payload received")
            return jsonify({"error": "Empty payload"}), 400
            
        # Extract content from either email_body or text (Mailparser sometimes uses different keys)
        email_body = payload.get('email_body', payload.get('text', ''))
        pdf_text = payload.get('pdf_text', '')
        
        if not email_body and not pdf_text:
            logger.error("No content found in payload")
            return jsonify({"error": "No content provided"}), 400
            
        # Combine content with source labels
        combined_text = ""
        if email_body:
            combined_text += f"EMAIL CONTENT:\n{email_body}\n\n"
        if pdf_text:
            combined_text += f"PDF CONTENT:\n{pdf_text}\n"
        
        logger.debug(f"Processing text (first 200 chars): {combined_text[:200]}...")
        
        # Extract structured data
        result = extract_invoice_data(combined_text)
        
        # Handle error responses
        if "error" in result:
            logger.error(f"Processing failed: {result['error']}")
            return jsonify(result), 400
            
        # Successful response
        logger.info("Invoice data extracted successfully")
        response = {
            "status": "success",
            "data": result,
            "source": "email_only" if not pdf_text else "email_with_pdf"
        }
        
        # Return pretty-printed JSON in debug mode
        if Config.DEBUG:
            return jsonify(response), 200, {
                'Content-Type': 'application/json; charset=utf-8',
                'X-Content-Type-Options': 'nosniff'
            }
        return jsonify(response)
        
    except Exception as e:
        logger.exception("Error processing webhook")
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)