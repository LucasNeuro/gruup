import os
from mistralai import Mistral
from dotenv import load_dotenv
load_dotenv()

# Substitua pelo seu ID de agente real se tiver, ou use um modelo de chat comum para emular
AGENT_ID = os.environ.get("MISTRAL_AGENT_ID", "ag_019b9ab1506d711190e15e488046d081") 
API_KEY = os.environ.get("MISTRAL_API_KEY")

client = Mistral(api_key=API_KEY)

def test_agent(message):
    print(f"User: {message}")
    
    try:
        # Tenta usar a API de Agentes (Beta)
        response = client.agents.complete(
            agent_id=AGENT_ID,
            messages=[{"role": "user", "content": message}]
        )
        print(f"Agent: {response.choices[0].message.content}")
    except Exception as e:
        print(f"Erro (talvez o ID do agente esteja inválido ou API indisponível): {e}")

if __name__ == "__main__":
    test_agent("Olá, gostaria de saber sobre planos de internet")
