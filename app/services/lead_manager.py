from app.services.supabase_client import get_supabase_client
from app.services.mistral_client import analyze_lead_message, generate_handover_summary
import random

supabase = get_supabase_client()

    # ... Imports
    from app.services.mistral_client import chat_with_agent, generate_handover_summary
    
    # ... (Dentro de process_message)
    
    # Busca histórico para contexto
    h_response = supabase.table("historico_conversas").select("mensagem, direcao").eq("lead_id", lead_id).order("created_at", desc=False).limit(20).execute()
    
    history_messages = []
    if h_response.data:
        for item in h_response.data:
            role = "user" if item["direcao"] == "in" else "assistant"
            history_messages.append({"role": role, "content": item["mensagem"]})
            
    # Chama Agente
    agent_result = chat_with_agent(message_text, history_messages)
    
    # Salva interação do Agente no histórico
    if agent_result["response"]:
        log_ai = {
            "lead_id": lead_id,
            "direcao": "out_ai", # Nova direção para identificar msg de IA
            "mensagem": agent_result["response"],
            "resumo_ia": ""
        }
        supabase.table("historico_conversas").insert(log_ai).execute()

    if agent_result["action"] == "continue":
        # Continua conversa automática (IA responde Lead)
        return {
            "action": "reply_to_lead",
            "message": agent_result["response"],
            "lead_whatsapp": whatsapp_lead
        }
    
    else:
        # Handover (Transfere para Vendedor)
        # Logica existente de escolha de vendedor...
        
        # ... (Mantém lógica de escolha de vendedor do código original aqui)
        # Escolhe vendedor, define context_message = agent_result["response"] ou um resumo
        
        # (Reutilizando a lógica existente abaixo, ajustada)

async def save_vendor_message(vendor_whatsapp: str, lead_whatsapp: str, message: str) -> dict:
    """
    Salva mensagem do vendedor no histórico de conversas.
    
    Args:
        vendor_whatsapp: Número do WhatsApp do vendedor
        lead_whatsapp: Número do WhatsApp do lead
        message: Texto da mensagem do vendedor
    
    Returns:
        dict com status da operação
    """
    try:
        # 1. Busca o lead pelo WhatsApp
        lead_response = supabase.table("leads").select("*").eq("whatsapp_lead", lead_whatsapp).execute()
        
        if not lead_response.data:
            return {"error": "Lead não encontrado", "lead_whatsapp": lead_whatsapp}
        
        lead = lead_response.data[0]
        lead_id = lead["id"]
        
        # 2. Verifica se o vendedor está atribuído a este lead
        vendedor_response = supabase.table("vendedores").select("*").eq("whatsapp_vendedor", vendor_whatsapp).execute()
        
        if not vendedor_response.data:
            return {"error": "Vendedor não encontrado", "vendor_whatsapp": vendor_whatsapp}
        
        vendedor = vendedor_response.data[0]
        
        if lead["vendedor_id"] != vendedor["id"]:
            return {
                "error": "Vendedor não está atribuído a este lead",
                "vendor_whatsapp": vendor_whatsapp,
                "lead_whatsapp": lead_whatsapp
            }
        
        # 3. Salva mensagem do vendedor no histórico (direcao: 'out')
        log_data = {
            "lead_id": lead_id,
            "direcao": "out",  # outgoing from vendor
            "mensagem": message,
            "resumo_ia": ""
        }
        
        result = supabase.table("historico_conversas").insert(log_data).execute()
        
        if result.data:
            return {
                "success": True,
                "message": "Mensagem do vendedor salva com sucesso",
                "lead_id": lead_id,
                "vendor_name": vendedor["nome"]
            }
        else:
            return {"error": "Erro ao salvar mensagem no histórico"}
            
    except Exception as e:
        print(f"Error saving vendor message: {e}")
        return {"error": str(e)}