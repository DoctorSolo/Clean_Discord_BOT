# src/AI.py
import ollama
from CONFIG.AI_CONFIG import AI_GENERAL_MODEL
from src.AI_TOOLS.AI_MEMORY import AI_Memory


class AI:
    
    # Here wake up the AI model with initial prompt and history memory
    def __init__(self, model: str, max_history: int = 15):
        
        self.client         = ollama.Client() # Instantiates a model here
        self.model          = model             # Set the AI model
        self.max_history    = max_history       # Define history lenght
    # END
    
    
    def generate(self, prompt: str, user_id: str = "global", user_name: str = "None", temperature: float = 0.7) -> str:
        """Método síncrono - será executado em thread separada"""
        
        ai_memory = AI_Memory()
        ai_memory.gerenciar_memoria(user_id, prompt, user_name)
        history = ai_memory.get_all_memories_formatted()
        
        try:
            # Timeout na chamada HTTP
            prompt_completo = f"""
            [INSTRUÇÕES DO SISTEMA]
                Você é o Clean, um bot de Discord amigável e engraçado.
                Diretrizes:
                - Respostas curtas, objetivas e no mesmo idioma do usuário.
                - Chame as pessoas pelo nome ({user_name}) quando couber naturalmente.
                - Se não souber de algo, seja honesto.
                - O histórico serve apenas como contexto; responda exclusivamente à "MENSAGEM ATUAL".

            [HISTÓRICO DA CONVERSA]
                {history}

            [MENSAGEM ATUAL DE {user_name}]
                {prompt}

            [RESPOSTA DO CLEAN]"""

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