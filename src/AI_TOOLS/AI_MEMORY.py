import ollama
import sqlite3
#from CONFIG.AI_CONFIG import AI_MEMORY_GENERATE


class AI_Memory:
    def __init__(self):
        # Configuração do Banco de Dados (SQLite) para múltiplos usuários
        self.conn = sqlite3.connect('memorias.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS memorias (user_id TEXT PRIMARY KEY, memoria TEXT)')
        self.conn.commit()
    # END
    
    
    def __str__(self):
        return f"{self.new_memory}"
    

    def gerenciar_memoria(self, user_id: str, nova_fala: str, user_name: str) -> str:
        memoria_atual = self.get_memory(user_id)
        
        prompt = f"""
            Você é o componente de gerenciamento de memória de longo prazo de um assistente virtual.
            Sua única função é manter um registro de fatos permanentes sobre o usuário.

            ## ENTRADA
            - user_id: {user_id}
            - user_name: {user_name}
            - memoria_atual: {memoria_atual}
            - nova_fala: {nova_fala}

            ## TAREFA
            Atualize a memória integrando a nova fala à memória existente.

            ## REGRAS
            1. Extraia APENAS fatos duradouros: identidade, preferências estáveis, dados biográficos, restrições permanentes.
            2. IGNORE: cumprimentos, perguntas, comandos, conversa casual, informações efêmeras (humor momentâneo, clima, etc).
            3. Em caso de conflito sobre o MESMO atributo, o novo fato substitui o antigo. Fatos sobre atributos diferentes coexistem.
            4. Preserve todos os fatos antigos que NÃO foram contraditos.
            5. NÃO responda ao usuário, NÃO justifique, NÃO comente.

            ## FORMATO DE SAÍDA
            Responda APENAS com JSON válido, sem markdown:
            {{"memoria": "<fatos separados por ponto e vírgula, em uma linha>"}}

            Se não houver NENHUM fato duradouro (nem na memória atual nem na nova fala):
            {{"memoria": "VAZIO"}}

            ## EXEMPLOS

            Exemplo 1 — adiciona fato:
            memoria_atual: "Usuário mora em SP."
            nova_fala: "Meu aniversário é dia 12 de março."
            saída: {{"memoria": "Usuário mora em SP; aniversário em 12 de março."}}

            Exemplo 2 — substitui fato conflitante:
            memoria_atual: "Usuário mora em SP."
            nova_fala: "Acabei de me mudar para o Rio."
            saída: {{"memoria": "Usuário mora no Rio."}}

            Exemplo 3 — nada relevante:
            memoria_atual: "Usuário mora em SP."
            nova_fala: "Bom dia! Tudo bem?"
            saída: {{"memoria": "Usuário mora em SP."}}

            Exemplo 4 — memória vazia e nada relevante:
            memoria_atual: ""
            nova_fala: "Oi, tudo bem?"
            saída: {{"memoria": "VAZIO"}}
            """

        # 3. Consulta o Ollama
        response = ollama.chat(model='gemma4', messages=[{'role': 'user', 'content': prompt}],)
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


    def get_all_memories_formatted(self) -> str:
        # Busca o ID do usuário e a memória associada
        self.cursor.execute("SELECT user_id, memoria FROM memorias")
        resultados = self.cursor.fetchall()

        if not resultados:
            return "Nenhuma memória registrada no sistema."

        # Formata cada registro para fácil interpretação pelo modelo
        linhas = [
            f"- Usuário {user_id}: {memoria.strip()}"
            for user_id, memoria in resultados
            if memoria
        ]

        return "### Memórias do Sistema:\n" + "\n".join(linhas)
    # END

# if __name__ == "__main__":
#     print("1. Pedro:", AI_Memory("pedro", "Eu gosto de banana"))
#     print("1. Pedro:", AI_Memory("pedro", "Eu não gosto de banana"))
#     print("2. Maria:", AI_Memory("maria", "Eu adoro maçã"))
#     print("2. Maria:", AI_Memory("maria", "Eu adoro uvas também"))
#     print("2. Maria:", AI_Memory("maria", "Meu apelido é Mari"))