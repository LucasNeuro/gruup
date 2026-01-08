from mistralai import Mistral
from app.config import MISTRAL_API_KEY, MISTRAL_AGENT_ID
import json

client = Mistral(api_key=MISTRAL_API_KEY)

def chat_with_agent(message: str, history: list = None) -> dict:
    """
    Envia mensagem para o Agente Mistral e processa a resposta.
    Retorna dict com 'response' (texto) e 'action' (continue/handover).
    """
    if history is None:
        history = []
        
    # Adiciona mensagem atual
    messages = history + [{"role": "user", "content": message}]
    
    try:
        # Chama a API de Agentes
        # Nota: agent_id é passado aqui. 
        # Esta é a chamada correta para a API v1 de Agentes (agents.complete)
        response = client.agents.complete(
            agent_id=MISTRAL_AGENT_ID,
            messages=messages
        )
        
        agent_response = response.choices[0].message.content
        
        # Lógica simples de detecção de transbordo no texto do agente
        # O agente deve ser instruído a usar [TRANSFER_TO_HUMAN] ou similar
        # Se não, podemos tentar detectar intenção aqui também.
        
        action = "continue"
        if "[TRANSFER_TO_HUMAN]" in agent_response:
            action = "handover"
            # Remove a tag da resposta visível ao usuário, se desejar limpar
            clean_response = agent_response.replace("[TRANSFER_TO_HUMAN]", "").strip()
        else:
            clean_response = agent_response
            
        return {
            "response": clean_response,
            "action": action,
            "raw_response": agent_response
        }

    except Exception as e:
        print(f"Error calling Mistral Agent: {e}")
        return {
            "response": "Desculpe, estou com dificuldade de conexão no momento. Um atendente irá ajudá-lo em breve.",
            "action": "handover" # Falha segura para humano
        }

# Mantendo compatibilidade com código antigo (opcional, pode ser removido se lead_manager for atualizado totalmente)
def analyze_lead_message(message: str) -> dict:
    # Usa o agente para analisar também
    result = chat_with_agent(f"Analise esta mensagem como triagem e retorne JSON: {message}")
    # Tenta extrair JSON se o agente retornar JSON
    try:
        start = result["raw_response"].find("{")
        end = result["raw_response"].rfind("}") + 1
        if start != -1 and end != -1:
            return json.loads(result["raw_response"][start:end])
    except:
        pass
    return {"interesse": "Geral (Agente)", "resumo": result["response"]}

def generate_handover_summary(lead_name: str, history: str) -> str:
    # Usa agente para resumir
    prompt = f"Gere resumo de handover para vendedor sobre {lead_name}. Histórico: {history}"
    result = chat_with_agent(prompt)
    return result["response"]
