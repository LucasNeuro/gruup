from app.services.supabase_client import get_supabase_client
from app.services.mistral_client import analyze_lead_message, generate_handover_summary
import random

supabase = get_supabase_client()

async def process_message(payload: dict):
    # Extract data from Uazapi/Make payload
    # Assuming payload structure: {"sender_pn": "5511999999999", "message": "Olá, quero internet", "name": "Nome Lead"}
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
    is_new_lead = False
    
    if leads:
        # Existing Lead
        lead = leads[0]
        lead_id = lead["id"]
        vendedor_id = lead["vendedor_id"]
        
        # Fetch assigned vendor details
        v_response = supabase.table("vendedores").select("*").eq("id", vendedor_id).execute()
        if v_response.data:
            vendedor = v_response.data[0]
            vendedor_nome = vendedor["nome"]
            vendedor_whatsapp = vendedor["whatsapp_vendedor"]
            
    else:
        # New Lead
        is_new_lead = True
        
        # Analyze first message with AI
        analysis = analyze_lead_message(message_text)
        nome_ia = f"{lead_name} ({analysis.get('interesse', 'Lead')})"
        
        # Assign Vendor (Round Robin / Random for MVP)
        # Select active vendors
        v_response = supabase.table("vendedores").select("*").eq("ativo", True).execute()
        active_vendors = v_response.data
        
        if not active_vendors:
            return {"action": "error", "message": "No active vendors found"}
            
        # Simple random assignment for MVP
        chosen_vendor = random.choice(active_vendors)
        vendedor_id = chosen_vendor["id"]
        vendedor_nome = chosen_vendor["nome"]
        vendedor_whatsapp = chosen_vendor["whatsapp_vendedor"]
        
        # Create Lead
        new_lead_data = {
            "whatsapp_lead": whatsapp_lead,
            "nome_ia": nome_ia,
            "vendedor_id": vendedor_id,
            "status": "novo"
        }
        l_response = supabase.table("leads").insert(new_lead_data).execute()
        if l_response.data:
            lead_id = l_response.data[0]["id"]
    
    # 2. Log Conversation
    # AI summary of this specific message (optional, or rely on accumulated context)
    # For now, we log the raw message.
    log_data = {
        "lead_id": lead_id,
        "direcao": "in", # incoming from lead
        "mensagem": message_text,
        "resumo_ia": "" # Could populate if we ran specific per-message analysis needed for log
    }
    supabase.table("historico_conversas").insert(log_data).execute()
    
    # 3. Formulate Response for Make
    
    if is_new_lead:
       context_message = f"Novo Lead! {lead_name} acabou de mandar mensagem: '{message_text}'. Interesse: {analysis.get('interesse')}."
    else:
        # Fetch recent history to generate summary
        h_response = supabase.table("historico_conversas").select("mensagem, direcao").eq("lead_id", lead_id).order("created_at", desc=True).limit(5).execute()
        history_text = "\n".join([f"{h['direcao']}: {h['mensagem']}" for h in h_response.data])
        
        summary = generate_handover_summary(lead_name, history_text)
        context_message = f"Cliente retornou: {summary}"

    return {
        "action": "forward_to_vendor",
        "vendor_whatsapp": vendedor_whatsapp,
        "vendor_name": vendedor_nome,
        "context": context_message,
        "lead_whatsapp": whatsapp_lead
    }

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