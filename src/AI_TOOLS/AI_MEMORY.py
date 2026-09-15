import ollama
import sqlite3
#from CONFIG.AI_CONFIG import AI_MEMORY_GENERATE


class AI_Memory:
    def __init__(self, user_id: str, prompt: str):
        # Configuração do Banco de Dados (SQLite) para múltiplos usuários
        self.conn = sqlite3.connect('memorias.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS memorias (user_id TEXT PRIMARY KEY, memoria TEXT)')
        self.conn.commit()
        
        self.new_memory = self.gerenciar_memoria(user_id, prompt)
    # END
    
    
    def __str__(self):
        return f"{self.new_memory}"
    

    def gerenciar_memoria(self, user_id: str, nova_fala: str) -> str:
        memoria_atual = self.get_memory(user_id)

        # 2. Prompt para a IA extrair, resumir e atualizar/contradizer a memória
        # prompt = f"""
        # Você é o módulo de memória de uma IA. 
        # Usuário: {user_id}
        # Memória atual: "{memoria_atual}"
        # Nova fala do usuário: "{nova_fala}"
        
        # Tarefa: Atualize a memória de forma resumida e conservadora. 
        # - Se a nova fala contradiz a memória atual, substitua a informação antiga (ex: "gosta" vira "não gosta").
        # - Se a nova fala anula a memória sem adicionar nada novo, retorne a palavra VAZIO.
        # - Responda APENAS com a nova memória em uma única frase curta, ou a palavra VAZIO. Não dê explicações.
        # """
        
        prompt = f"""
            Você é o módulo de memória de uma IA. 
            Usuário: {user_id}
            Memória atual: "{memoria_atual}"
            Nova fala do usuário: "{nova_fala}"
            
            Tarefa: Atualize a memória de forma resumida e conservadora. 
            - Se a nova fala contradiz a memória atual, substitua a informação antiga (ex: "gosta" vira "não gosta").
            - Se a nova fala anula a memória sem adicionar nada novo, retorne a palavra VAZIO.
            - Responda APENAS em uma única frase curta, ou a palavra VAZIO. Não dê explicações.
            """

        # 3. Consulta o Ollama
        response = ollama.chat(model='gamma4', messages=[{'role': 'user', 'content': prompt}],)
        nova_memoria = response['message']['content'].strip()

        # 4. Salva ou apaga no banco de dados
        if nova_memoria.upper() == "VAZIO" or not nova_memoria:
            self.cursor.execute('DELETE FROM memorias WHERE user_id=?', (user_id,))
            self.conn.commit()
            return "Memória apagada."
        
        self.cursor.execute('INSERT OR REPLACE INTO memorias (user_id, memoria) VALUES (?, ?)', (user_id, nova_memoria))
        self.conn.commit()
        
        return nova_memoria
    # END
    
    
    def get_memory(self, user_id: str):
        # 1. Busca a memória atual do usuário específico
        self.cursor.execute('SELECT memoria FROM memorias WHERE user_id=?', (user_id,))
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else "Nenhuma"
    # END


if __name__ == "__main__":
    print("1. Pedro:", AI_Memory("pedro", "Eu gosto de banana"))
    print("2. Maria:", AI_Memory("maria", "Eu adoro maçã"))
    print("2. Maria:", AI_Memory("maria", "Eu adoro uvas também"))