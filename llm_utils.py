from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from schemas import InvoiceData, PartialInvoiceData
from config import Config
import logging
import json

logger = logging.getLogger(__name__)

def extract_invoice_data(text: str) -> dict:
    """Extract structured invoice data using LLM with fallback handling"""
    try:
        if not getattr(Config, 'GROQ_API_KEY', None):
            logger.error("GROQ_API_KEY is missing in Config.")
            return {"error": "GROQ API key is not configured."}

        # First try with strict validation
        try:
            parser = PydanticOutputParser(pydantic_object=InvoiceData)
            prompt = get_prompt_template(parser)
            model = get_groq_model()
            chain = prompt | model | parser
            result = chain.invoke({
                "text": text,
                "format_instructions": parser.get_format_instructions()
            })
            return result.dict()
        except Exception as strict_error:
            logger.warning(f"Strict parsing failed, trying partial mode: {strict_error}")
            
            # Fallback to partial validation
            try:
                partial_parser = PydanticOutputParser(pydantic_object=PartialInvoiceData)
                prompt = get_prompt_template(partial_parser)
                model = get_groq_model()
                chain = prompt | model | partial_parser
                result = chain.invoke({
                    "text": text,
                    "format_instructions": partial_parser.get_format_instructions()
                })
                return result.dict()
            except Exception as partial_error:
                logger.error(f"Partial parsing failed: {partial_error}")
                return {
                    "error": "Failed to parse invoice data",
                    "details": str(partial_error),
                    "llm_input": text[:500] + "..." if len(text) > 500 else text
                }

    except Exception as e:
        logger.exception("LLM extraction failed")
        return {"error": f"Failed to extract invoice data: {str(e)}"}

def get_prompt_template(parser):
    return ChatPromptTemplate.from_template(
        """Extract invoice data from this text exactly matching this schema.
        Return ONLY valid JSON, no explanations, no markdown, no code blocks.
        For missing fields, use null. Convert all amounts to numbers.
        
        Schema Instructions:
        {format_instructions}
        
        Text to parse:
        {text}
        
        Output ONLY the JSON object:"""
    )

def get_groq_model():
    return ChatGroq(
        model_name="llama3-70b-8192",
        temperature=0,
        groq_api_key=Config.GROQ_API_KEY
    )