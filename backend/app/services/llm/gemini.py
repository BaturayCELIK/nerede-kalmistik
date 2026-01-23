import google.generativeai as genai
from app.services.llm.base import BaseLLMClient
import os
from dotenv import load_dotenv
load_dotenv()
class GeminiClient(BaseLLMClient):

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_KEY"))
        # Modeli başlatıyoruz (Gemini 2.5 Flash hızlı ve ücretsiz katman için idealdir)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            generation_config={
                "temperature": 0.4,
            },
            # System prompt burada tanımlanır
            system_instruction="You are a professional TV series recap writer."
        )

    def generate_recap(self, prompt: str) -> str:
        # Gemini'de mesaj gönderme yapısı
        response = self.model.generate_content(prompt)
        
        # Yanıtı döndür
        return response.text