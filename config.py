import os 
from dotenv import load_dotenv 
load_dotenv() 

class Config: 
    GROQ_API_KEY = os.getenv('GROQ_API_KEY') 
    PORT = int(os.getenv('PORT', 5000)) 
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true' 