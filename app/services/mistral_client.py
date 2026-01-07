from mistralai import Mistral
from app.config import MISTRAL_API_KEY
import json

client = Mistral(api_key=MISTRAL_API_KEY)

def analyze_lead_message(message: str) -> dict:
    prompt = f"""
    Analise a seguinte mensagem de um lead e extraia informações relevantes para um perfil de vendas.
    Mensagem: "{message}"
    
    Retorne APENAS um JSON com os seguintes campos:
    - resumo: Um breve resumo da necessidade do cliente.
    - interesse: O produto ou serviço que ele parece querer.
    - urgencia: 'Alta', 'Média' ou 'Baixa'.
    - sentimento: 'Positivo', 'Neutro' ou 'Negativo'.
    """
    
    messages = [
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    try:
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        content = chat_response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing Mistral response: {e}")
        return {
            "resumo": "Erro ao analisar mensagem",
            "interesse": "Desconhecido",
            "urgencia": "Média",
            "sentimento": "Neutro"
        }

def generate_handover_summary(lead_name: str, history: str) -> str:
    prompt = f"""
    Gere um resumo curto para o vendedor sobre o lead {lead_name}.
    Histórico recente:
    {history}
    
    O resumo deve ser direto e útil para o vendedor iniciar o atendimento.
    Exemplo: "O cliente quer fibra 500mb, está insatisfeito com a atual."
    """
    
    messages = [
        {
            "role": "user", 
            "content": prompt
        }
    ]
    
    try:
        chat_response = client.chat.complete(
            model="mistral-large-latest",
            messages=messages
        )
        
        return chat_response.choices[0].message.content
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Não foi possível gerar o resumo."
