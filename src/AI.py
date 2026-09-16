# src/AI.py
import ollama
from CONFIG.AI_CONFIG import AI_GENERAL_MODEL
import json
import toon
import time
from typing import Optional
from src.AI_TOOLS.AI_MEMORY import AI_Memory


class AI:
    
    # Here wake up the AI model with initial prompt and history memory
    def __init__(self, model: str, max_history: int = 15):
        
        self.client         = ollama.Client() # Instantiates a model here
        self.model          = model             # Set the AI model
        self.max_history    = max_history       # Define history lenght
        
        self.user_histories = {} # History per user
        
        # Here this the most import main prompt, It's initiate with this prompt first!
        self.system_prompt = """Você é um bot de Discord chamado Clean.
        
        Características:
        - Você é amigável e engraçado.
        - Você usa respostas curtas e objetivas.
        - Você chama as pessoas pelo nome quando sabe.
        - Se não souber algo, diga honestamente.
        - Responda no mesmo idioma do usuário."""
    # END
    
    
    def generate(self, prompt: str, user_id: str = "global", temperature: float = 0.7) -> str:
        """Método síncrono - será executado em thread separada"""
        
        history = AI_Memory(user_id, prompt).get_memory(user_id)
        
        try:
            # Timeout na chamada HTTP
            prompt_completo = f"""Histórico do usuário {user_id}:
            {history}

            Pergunta atual:
            {prompt}"""

            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt_completo}],
                options={
                    "temperature": temperature,
                    "num_predict": 512,
                    "top_p": 0.9,
                },
            )
            
            bot_response = response['message']['content']
            return bot_response
            
        except Exception as e:
            return f"❌ Erro na IA: {str(e)}"
    # END


NEXUS_AI = AI(model=AI_GENERAL_MODEL)