# src/Bot.py
import discord
from discord.ext import commands
from src.AI import NEXUS_AI
import json
import asyncio


class Bot:
    def __init__(self, token: str):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        
        self.bot = commands.Bot(command_prefix="!", intents=intents)
        
        self.setup_events()
        
        self.bot.run(token)
    
    
    def setup_events(self):
        @self.bot.event
        async def on_ready():
            print(f'✅ Bot conectado como {self.bot.user.name}')
            
        
        @self.bot.event
        async def on_message(msg: discord.Message):
            # Ignora mensagens do próprio bot
            if msg.author.bot:
                return
            
            # Processa comandos primeiro (sempre)
            await self.bot.process_commands(msg)
            
            
            # 🔥 RESPONDE A TODAS AS MENSAGENS (sem verificar menção)
            user_name = msg.author.display_name or msg.author.name
            user_id = str(msg.author.id)
            
            # Contexto da mensagem
            context = msg.content
            
            # Mostra que o bot está processando
            async with msg.channel.typing():
                try:
                    # Gera resposta com IA
                    response = await self.generate_ai_response(
                        prompt=context,
                        user_id=user_id,
                        user_name=user_name
                    )
                    
                    # Envia a resposta
                    if len(response) > 2000:
                        for i in range(0, len(response), 2000):
                            await msg.channel.send(response[i:i+2000])
                    else:
                        await msg.reply(response, mention_author=False)
                        
                except Exception as e:
                    await msg.channel.send(f"❌ Erro ao processar: {str(e)}")
                    print(f"Erro no on_message: {e}")
        
    
    async def generate_ai_response(self, prompt: str, user_id: str, user_name: str) -> str:
        """Executa a chamada ao Ollama em thread separada"""
        try:
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    NEXUS_AI.generate,
                    prompt=prompt,
                    user_id=user_id,
                    user_name=user_name
                ),
                timeout=120.0  # 60 segundos de timeout
            )
            return response
        except asyncio.TimeoutError:
            return "⏰ A IA está demorando para responder. Tente novamente em alguns instantes."
        except Exception as e:
            return f"❌ Erro na IA: {str(e)}"

# Inicialização
if __name__ == "__main__":
    from CONFIG.config import DISCORD_TOKEN
    bot = Bot(token=DISCORD_TOKEN)