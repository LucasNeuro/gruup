from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List
from app.services.lead_manager import process_message, save_vendor_message

app = FastAPI(
    title="CRM Brain API",
    description="API para processamento inteligente de leads via WhatsApp com distribuição automática para vendedores",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI em /docs
    redoc_url="/redoc"  # ReDoc em /redoc
)

# Modelos para o formato Uazapi/Make
class UazapiMessage(BaseModel):
    sender_pn: Optional[str] = None
    text: Optional[str] = None
    content: Optional[str] = None
    senderName: Optional[str] = None
    messageType: Optional[str] = None
    chatid: Optional[str] = None

class UazapiChat(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    wa_name: Optional[str] = None
    wa_contactName: Optional[str] = None
    wa_lastMessageTextVote: Optional[str] = None

class UazapiWebhookItem(BaseModel):
    BaseUrl: Optional[str] = None
    EventType: Optional[str] = None
    chat: Optional[UazapiChat] = None
    message: Optional[UazapiMessage] = None
    owner: Optional[str] = None
    token: Optional[str] = None
    instanceName: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "BaseUrl": "https://atendemais.uazapi.com",
                "EventType": "messages",
                "chat": {
                    "name": "Lucas",
                    "phone": "+55 11 97036-4501",
                    "wa_name": "Lucas Marcondès",
                    "wa_contactName": "Lucas",
                    "wa_lastMessageTextVote": "Preciso de uma internet pra minha residencia"
                },
                "message": {
                    "sender_pn": "5511970364501@s.whatsapp.net",
                    "text": "Preciso de uma internet pra minha residencia",
                    "content": "Preciso de uma internet pra minha residencia",
                    "senderName": "Lucas Marcondès"
                },
                "owner": "5511914589862",
                "instanceName": "CAIXA_01",
                "token": "99373875-7f07-49cb-9ad8-466d6d37b313"
            }
        }

# Modelo simplificado para testes diretos no Swagger
class SimpleWebhookPayload(BaseModel):
    sender_pn: str
    message: str
    name: Optional[str] = "Desconhecido"
    
    class Config:
        json_schema_extra = {
            "example": {
                "sender_pn": "5511970364501",
                "message": "Preciso de uma internet pra minha residencia",
                "name": "Lucas"
            }
        }

# Modelo para mensagem do vendedor
class VendorMessagePayload(BaseModel):
    vendor_whatsapp: str
    lead_whatsapp: str
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "vendor_whatsapp": "5511999999999",
                "lead_whatsapp": "5511970364501",
                "message": "Olá! Como posso ajudar você hoje?"
            }
        }

def extract_lead_data_from_uazapi(item: UazapiWebhookItem) -> dict:
    """Extrai dados do lead do formato Uazapi"""
    message_obj = item.message or UazapiMessage()
    chat_obj = item.chat or UazapiChat()
    
    # Extrai número do WhatsApp (remove @s.whatsapp.net se presente)
    sender_pn = message_obj.sender_pn or chat_obj.phone or ""
    if sender_pn and "@" in sender_pn:
        sender_pn = sender_pn.split("@")[0]
    # Remove caracteres não numéricos, exceto +
    if sender_pn:
        sender_pn = ''.join(c for c in sender_pn if c.isdigit() or c == '+')
    
    # Extrai mensagem
    message_text = message_obj.text or message_obj.content or chat_obj.wa_lastMessageTextVote or ""
    
    # Extrai nome
    lead_name = (message_obj.senderName or chat_obj.name or 
                chat_obj.wa_name or chat_obj.wa_contactName or "Desconhecido")
    
    return {
        "sender_pn": sender_pn,
        "message": message_text,
        "name": lead_name
    }

@app.post("/v1/brain", 
          summary="Processa mensagem de lead (Webhook Uazapi/Make)",
          description="""
          **Endpoint principal para webhooks do Make/Integromat com Uazapi**
          
          Recebe mensagem de lead no formato do webhook Uazapi/Make.
          Este é o endpoint que deve ser configurado no Make/Integromat.
          
          O formato esperado é um array com objetos contendo `chat` e `message`.
          """,
          response_description="Retorna ação para encaminhar ao vendedor com contexto")
async def brain_webhook(
    payload: List[UazapiWebhookItem] = Body(
        ...,
        example=[{
            "BaseUrl": "https://atendemais.uazapi.com",
            "EventType": "messages",
            "chat": {
                "name": "Lucas",
                "phone": "+55 11 97036-4501",
                "wa_name": "Lucas Marcondès",
                "wa_contactName": "Lucas",
                "wa_lastMessageTextVote": "Preciso de uma internet pra minha residencia"
            },
            "message": {
                "sender_pn": "5511970364501@s.whatsapp.net",
                "text": "Preciso de uma internet pra minha residencia",
                "content": "Preciso de uma internet pra minha residencia",
                "senderName": "Lucas Marcondès"
            },
            "owner": "5511914589862",
            "instanceName": "CAIXA_01",
            "token": "99373875-7f07-49cb-9ad8-466d6d37b313"
        }]
    )
):
    """
    Endpoint para webhook do Uazapi/Make.
    Aceita array de objetos UazapiWebhookItem.
    """
    try:
        if not payload or len(payload) == 0:
            raise HTTPException(status_code=400, detail="Array vazio. Esperado array com pelo menos um item.")
        
        # Processa o primeiro item do array
        item = payload[0]
        processed_payload = extract_lead_data_from_uazapi(item)
        
        if not processed_payload.get("sender_pn"):
            raise HTTPException(status_code=400, detail="Não foi possível extrair o número do WhatsApp (sender_pn)")
        
        if not processed_payload.get("message"):
            raise HTTPException(status_code=400, detail="Não foi possível extrair a mensagem")
        
        result = await process_message(processed_payload)
        return result
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/brain/simple",
          summary="Processa mensagem de lead (Formato Simplificado)",
          description="Endpoint alternativo para testes com formato simplificado. Use este para testar facilmente no Swagger.",
          response_description="Retorna ação para encaminhar ao vendedor com contexto")
async def brain_webhook_simple(payload: SimpleWebhookPayload):
    """
    Endpoint simplificado para testes no Swagger.
    Use este endpoint para testar rapidamente sem precisar do formato completo do Uazapi.
    """
    try:
        result = await process_message(payload.model_dump())
        return result
    except Exception as e:
        print(f"Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/vendor-message",
          summary="Salva mensagem do vendedor",
          description="""
          **Endpoint para salvar mensagens enviadas pelo vendedor ao lead**
          
          Quando o vendedor responde ao lead via WhatsApp, este endpoint deve ser chamado
          para salvar a mensagem no histórico de conversas (direcao: 'out').
          
          **Uso no Make/Integromat:**
          - Configure um webhook do Uazapi para capturar mensagens do vendedor
          - Identifique que a mensagem veio de um vendedor (não de um lead)
          - Chame este endpoint com os dados da mensagem
          """,
          response_description="Confirmação de salvamento da mensagem")
async def vendor_message_webhook(payload: VendorMessagePayload):
    """
    Endpoint para salvar mensagens do vendedor no histórico.
    """
    try:
        result = await save_vendor_message(
            payload.vendor_whatsapp,
            payload.lead_whatsapp,
            payload.message
        )
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing vendor message: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", 
         summary="Health Check",
         description="Endpoint para verificar se a API está funcionando")
def read_root():
    return {"status": "ok", "service": "CRM Brain Active"}
