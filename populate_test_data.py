"""
Script Python para popular dados de teste no banco Supabase
Execute: python populate_test_data.py
"""

import os
from dotenv import load_dotenv
from app.services.supabase_client import get_supabase_client

load_dotenv()

def populate_vendors():
    """Popula a tabela de vendedores com dados de teste"""
    supabase = get_supabase_client()
    
    # Vendedores de teste
    vendedores = [
        {
            "nome": "João Silva",
            "whatsapp_vendedor": "5511999999999",
            "ativo": True
        },
        {
            "nome": "Maria Santos",
            "whatsapp_vendedor": "5511888888888",
            "ativo": True
        },
        {
            "nome": "Pedro Oliveira",
            "whatsapp_vendedor": "5511777777777",
            "ativo": True
        },
        {
            "nome": "Ana Costa",
            "whatsapp_vendedor": "5511666666666",
            "ativo": True
        }
    ]
    
    print("🔄 Inserindo vendedores de teste...")
    
    for vendedor in vendedores:
        try:
            # Verifica se já existe pelo WhatsApp
            existing = supabase.table("vendedores").select("*").eq("whatsapp_vendedor", vendedor["whatsapp_vendedor"]).execute()
            
            if existing.data:
                print(f"   ⚠️  Vendedor {vendedor['nome']} já existe, pulando...")
            else:
                result = supabase.table("vendedores").insert(vendedor).execute()
                if result.data:
                    print(f"   ✅ Vendedor {vendedor['nome']} inserido com sucesso!")
        except Exception as e:
            print(f"   ❌ Erro ao inserir {vendedor['nome']}: {e}")
    
    # Lista todos os vendedores
    print("\n📋 Vendedores cadastrados:")
    all_vendors = supabase.table("vendedores").select("*").execute()
    for v in all_vendors.data:
        status = "✅ Ativo" if v.get("ativo") else "❌ Inativo"
        print(f"   • {v['nome']} - {v['whatsapp_vendedor']} - {status}")

def populate_sample_lead():
    """(Opcional) Cria um lead de teste já atribuído a um vendedor"""
    supabase = get_supabase_client()
    
    # Busca um vendedor ativo
    vendedores = supabase.table("vendedores").select("*").eq("ativo", True).limit(1).execute()
    
    if not vendedores.data:
        print("⚠️  Nenhum vendedor ativo encontrado. Crie vendedores primeiro.")
        return
    
    vendedor = vendedores.data[0]
    
    lead_teste = {
        "whatsapp_lead": "5511970364501",
        "nome_ia": "Lucas (Internet - Teste)",
        "vendedor_id": vendedor["id"],
        "status": "novo"
    }
    
    try:
        # Verifica se já existe
        existing = supabase.table("leads").select("*").eq("whatsapp_lead", lead_teste["whatsapp_lead"]).execute()
        
        if existing.data:
            print(f"⚠️  Lead {lead_teste['whatsapp_lead']} já existe.")
        else:
            result = supabase.table("leads").insert(lead_teste).execute()
            if result.data:
                print(f"✅ Lead de teste criado: {lead_teste['nome_ia']} atribuído a {vendedor['nome']}")
    except Exception as e:
        print(f"❌ Erro ao criar lead de teste: {e}")

if __name__ == "__main__":
    print("="*60)
    print("🚀 Populando dados de teste no banco")
    print("="*60 + "\n")
    
    populate_vendors()
    
    print("\n" + "="*60)
    resposta = input("\nDeseja criar um lead de teste também? (s/n): ").lower()
    if resposta == 's':
        populate_sample_lead()
    
    print("\n✅ Concluído!")
