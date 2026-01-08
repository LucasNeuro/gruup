from app.services.supabase_client import get_supabase_client
from app.services.mistral_client import chat_with_agent, generate_handover_summary
import random

supabase = get_supabase_client()

async def process_message(payload: dict):
    # Extract data from Uazapi/Make payload
    whatsapp_lead = payload.get("sender_pn")
    message_text = payload.get("message")
    lead_name = payload.get("name", "Desconhecido")
    
    if not whatsapp_lead:
        return {"error": "Missing sender_pn"}

    # 1. Check if lead exists
    response = supabase.table("leads").select("*").eq("whatsapp_lead", whatsapp_lead).execute()
    leads = response.data
    
    lead_id = None
    vendedor_id = None
    vendedor_nome = None
    vendedor_whatsapp = None
    
    if leads:
        lead = leads[0]
        lead_id = lead["id"]
        vendedor_id = lead.get("vendedor_id")
        
        # Se já tem vendedor, busca dados dele
        if vendedor_id:
            v_response = supabase.table("vendedores").select("*").eq("id", vendedor_id).execute()
            if v_response.data:
                vendedor = v_response.data[0]
                vendedor_nome = vendedor["nome"]
                vendedor_whatsapp = vendedor["whatsapp_vendedor"]
    else:
        # Cria lead novo
        new_lead_data = {
            "whatsapp_lead": whatsapp_lead,
            "nome_ia": f"{lead_name} (Novo)",
            "status": "novo"
        }
        l_response = supabase.table("leads").insert(new_lead_data).execute()
        if l_response.data:
            lead_id = l_response.data[0]["id"]
            
    # 2. Log Message (Lead)
    log_data = {
        "lead_id": lead_id,
        "direcao": "in",
        "mensagem": message_text,
        "resumo_ia": ""
    }
    supabase.table("historico_conversas").insert(log_data).execute()
    
    # 3. Build Context for Agent
    h_response = supabase.table("historico_conversas").select("mensagem, direcao").eq("lead_id", lead_id).order("created_at", desc=False).limit(20).execute()
    
    history_messages = []
    if h_response.data:
        for item in h_response.data:
            role = "user"
            # Se for saída (out), assumimos que foi o assistente ou vendedor falando
            if item["direcao"] == "out":
                role = "assistant"
                
            history_messages.append({"role": role, "content": item["mensagem"]})
            
    # 4. Agent Interaction
    agent_result = chat_with_agent(message_text, history_messages)
    
    # Salva resposta do Agente
    if agent_result.get("response"):
        log_ai = {
            "lead_id": lead_id,
            "direcao": "out", # Usando 'out' pois o banco tem restrição (check constraint)
            "mensagem": agent_result["response"],
            "resumo_ia": "Resposta Automática IA"
        }
        supabase.table("historico_conversas").insert(log_ai).execute()

    # 5. Decide Next Action
    if agent_result["action"] == "continue":
        return {
            "action": "reply_to_lead",
            "message": agent_result["response"],
            "lead_whatsapp": whatsapp_lead
        }
        
    else: 
        # HANDOVER logic
        if not vendedor_id:
             v_response = supabase.table("vendedores").select("*").eq("ativo", True).execute()
             active_vendors = v_response.data
             if active_vendors:
                 chosen_vendor = random.choice(active_vendors)
                 vendedor_id = chosen_vendor["id"]
                 vendedor_nome = chosen_vendor["nome"]
                 vendedor_whatsapp = chosen_vendor["whatsapp_vendedor"]
                 
                 # Atualiza lead com vendedor
                 supabase.table("leads").update({"vendedor_id": vendedor_id, "status": "atendimento"}).eq("id", lead_id).execute()
        
        context_message = agent_result["response"] 
        if not context_message:
            context_message = f"Cliente {lead_name} solicitou atendimento humano."

        return {
            "action": "forward_to_vendor",
            "vendor_whatsapp": vendedor_whatsapp,
            "vendor_name": vendedor_nome,
            "context": context_message,
            "lead_whatsapp": whatsapp_lead
        }

async def save_vendor_message(vendor_whatsapp: str, lead_whatsapp: str, message: str) -> dict:
    try:
        lead_response = supabase.table("leads").select("*").eq("whatsapp_lead", lead_whatsapp).execute()
        
        if not lead_response.data:
            return {"error": "Lead não encontrado", "lead_whatsapp": lead_whatsapp}
        
        lead = lead_response.data[0]
        lead_id = lead["id"]
        
        vendedor_response = supabase.table("vendedores").select("*").eq("whatsapp_vendedor", vendor_whatsapp).execute()
        
        if not vendedor_response.data:
            return {"error": "Vendedor não encontrado", "vendor_whatsapp": vendor_whatsapp}
        
        vendedor = vendedor_response.data[0]
        
        log_data = {
            "lead_id": lead_id,
            "direcao": "out",
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