from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from schemas import InvoiceData
from config import Config
import logging

logger = logging.getLogger(__name__)

def extract_invoice_data(text: str) -> dict:
    """Extract structured invoice data using LLM"""
    try:
        if not getattr(Config, 'GROQ_API_KEY', None):
            logger.error("GROQ_API_KEY is missing in Config.")
            return {"error": "GROQ API key is not configured."}

        parser = PydanticOutputParser(pydantic_object=InvoiceData)
        
        prompt = ChatPromptTemplate.from_template(
            "Extract invoice data from the following text. "
            "Return ONLY a single valid JSON object matching this schema, "
            "with no explanations, no markdown, and no code blocks. "
            "If a field is missing, use null. "
            "Schema:\n{format_instructions}\n"
            "Text:\n{text}\n"
        )
        
        model = ChatGroq(
            model_name="llama3-70b-8192",
            temperature=0,
            groq_api_key=Config.GROQ_API_KEY
        )
        
        chain = prompt | model | parser
        
        raw_chain = prompt | model
        raw_output = raw_chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions()
        })
        logger.debug(f"RAW LLM OUTPUT: {raw_output}")
        
        result = None
        try:
            result = parser.invoke(raw_output)
        except Exception as parse_err:
            logger.error(f"Parsing failed: {parse_err}")
            return {
                "error": f"Failed to parse LLM output: {parse_err}",
                "llm_output": str(raw_output)
            }
            
        if result is None:
            logger.error("LLM output is None after parsing.")
            return {
                "error": "LLM output is None after parsing.",
                "llm_output": str(raw_output)
            }
            
        return result.dict()
        
    except Exception as e:
        logger.error(f"LLM extraction failed: {str(e)}")
        return {"error": f"Failed to extract invoice data: {str(e)}"}