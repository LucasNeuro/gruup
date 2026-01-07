"""
Arquivo de inicialização da API CRM Brain
Execute: python run.py
"""

import uvicorn
import sys

def print_startup_info():
    """Exibe informações de acesso da API no console"""
    print("\n" + "="*60)
    print("🚀 CRM Brain API - Servidor Iniciado!")
    print("="*60)
    print("\n📍 URLs de Acesso:")
    print(f"   • API Base:        http://localhost:8000")
    print(f"   • Swagger UI:      http://localhost:8000/docs")
    print(f"   • ReDoc:           http://localhost:8000/redoc")
    print(f"   • Health Check:    http://localhost:8000/")
    print(f"   • Webhook Endpoint: http://localhost:8000/v1/brain")
    print("\n💡 Dica: Acesse http://localhost:8000/docs para testar a API")
    print("="*60 + "\n")

if __name__ == "__main__":
    # Imprime informações antes de iniciar
    print_startup_info()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload em desenvolvimento
        log_level="info"
    )
