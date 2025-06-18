from flask import Flask, request, jsonify
from llm_utils import extract_invoice_data
from config import Config
import logging
from datetime import datetime

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if Config.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('invoice_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle Mailparser webhook requests"""
    try:
        request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        logger.info(f"Request {request_id}: Received webhook")
        
        payload = request.json
        if not payload:
            logger.warning(f"Request {request_id}: Empty payload")
            return jsonify({
                "status": "error",
                "message": "Empty payload",
                "request_id": request_id
            }), 400
            
        # Extract content
        email_body = payload.get('email_body', '')
        pdf_text = payload.get('pdf_text', '')
        
        if not email_body and not pdf_text:
            logger.error(f"Request {request_id}: No content")
            return jsonify({
                "status": "error",
                "message": "No content provided",
                "request_id": request_id
            }), 400
            
        # Combine content
        combined_text = ""
        if email_body:
            combined_text += f"EMAIL CONTENT:\n{email_body}\n\n"
        if pdf_text:
            combined_text += f"PDF CONTENT:\n{pdf_text}"
        
        logger.debug(f"Request {request_id}: Processing text")
        
        # Extract invoice data
        result = extract_invoice_data(combined_text)
        
        if "error" in result:
            logger.error(f"Request {request_id}: Processing failed - {result['error']}")
            return jsonify({
                "status": "error",
                "message": result['error'],
                "request_id": request_id
            }), 400
            
        # Successful response
        logger.info(f"Request {request_id}: Invoice processed")
        response = {
            "status": "success",
            "request_id": request_id,
            "data": result,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(response), 200, {
            'Content-Type': 'application/json; charset=utf-8'
        }
        
    except Exception as e:
        logger.exception(f"Request {request_id}: Processing error")
        return jsonify({
            "status": "error",
            "message": str(e),
            "request_id": request_id
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)