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
        
        email_body = payload.get('email_body', '')
        pdf_text = payload.get('pdf_text', '')
        
        if not email_body and not pdf_text:
            logger.error("No content found in payload")
            return jsonify({"error": "No content provided"}), 400
        
        combined_text = f"EMAIL BODY:\n{email_body}\n\nPDF CONTENT:\n{pdf_text}"
        
        logger.debug(f"Processing text (first 500 chars): {combined_text[:500]}...")
        
        invoice_data = extract_invoice_data(combined_text)
        
        logger.info("Invoice data extracted successfully")
        logger.debug(f"Extracted data: {json.dumps(invoice_data, indent=2)}")
        
        return jsonify(invoice_data)
        
    except Exception as e:
        logger.exception("Error processing webhook")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)