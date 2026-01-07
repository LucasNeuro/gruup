# 🔄 Fluxo Completo do Sistema CRM Brain

## 📋 Visão Geral

O sistema gerencia a comunicação entre leads e vendedores, salvando todo o histórico de conversas.

---

## 🔀 Fluxo Passo a Passo

### 1️⃣ **Lead Envia Mensagem Inicial**

```
Lead (WhatsApp) → Uazapi → Make/Integromat → API /v1/brain
```

**O que acontece:**
- Lead envia mensagem no WhatsApp
- Uazapi captura e envia webhook para Make
- Make chama nossa API `/v1/brain`
- API processa:
  - ✅ Analisa mensagem com IA (interesse, urgência, sentimento)
  - ✅ Verifica se lead já existe
  - ✅ Se novo: atribui vendedor aleatoriamente
  - ✅ Salva mensagem do lead no histórico (`direcao: 'in'`)
  - ✅ Cria/atualiza lead no banco

**Resposta da API:**
```json
{
  "action": "forward_to_vendor",
  "vendor_whatsapp": "5511999999999",
  "vendor_name": "João Silva",
  "context": "Novo Lead! Lucas acabou de mandar mensagem: 'Preciso de internet'. Interesse: Internet.",
  "lead_whatsapp": "5511970364501"
}
```

---

### 2️⃣ **Make Encaminha para o Vendedor**

```
API Response → Make → Uazapi → Vendedor (WhatsApp)
```

**O que acontece:**
- Make recebe a resposta da API
- Make usa os dados para:
  - Enviar mensagem para o vendedor (`vendor_whatsapp`)
  - Incluir o contexto gerado pela IA
  - Informar o número do lead (`lead_whatsapp`)

**Exemplo de mensagem para vendedor:**
```
📱 Novo Lead!

Cliente: Lucas (5511970364501)
Contexto: Novo Lead! Lucas acabou de mandar mensagem: 'Preciso de internet'. Interesse: Internet.

Responda diretamente para: 5511970364501
```

---

### 3️⃣ **Vendedor Responde ao Lead**

```
Vendedor (WhatsApp) → Uazapi → Make → API /v1/vendor-message
```

**O que acontece:**
- Vendedor responde ao lead no WhatsApp
- Uazapi captura a mensagem do vendedor
- Make chama nossa API `/v1/vendor-message`
- API salva mensagem do vendedor no histórico (`direcao: 'out'`)

---

### 4️⃣ **Lead Responde de Volta**

```
Lead (WhatsApp) → Uazapi → Make → API /v1/brain
```

**O que acontece:**
- Lead responde ao vendedor
- Mesmo fluxo do passo 1, mas:
  - ✅ Lead já existe no banco
  - ✅ Busca histórico recente
  - ✅ Gera resumo com IA do contexto
  - ✅ Retorna para o mesmo vendedor atribuído
  - ✅ Salva nova mensagem (`direcao: 'in'`)

---

## 📊 Estrutura de Dados

### Tabela `historico_conversas`

| Campo | Valor | Descrição |
|-------|-------|-----------|
| `direcao` | `'in'` | Mensagem do lead para o vendedor |
| `direcao` | `'out'` | Mensagem do vendedor para o lead |
| `mensagem` | Texto | Conteúdo da mensagem |
| `lead_id` | UUID | Referência ao lead |
| `resumo_ia` | Texto | Resumo gerado pela IA (opcional) |

---

## 🔌 Endpoints da API

### `POST /v1/brain`
**Recebe mensagens do lead**

**Entrada:** Webhook Uazapi (array)
**Saída:** Dados para encaminhar ao vendedor

---

### `POST /v1/vendor-message`
**Recebe mensagens do vendedor**

**Entrada:**
```json
{
  "vendor_whatsapp": "5511999999999",
  "lead_whatsapp": "5511970364501",
  "message": "Olá! Como posso ajudar?"
}
```

**Saída:**
```json
{
  "success": true,
  "message": "Mensagem do vendedor salva com sucesso",
  "lead_id": "uuid-do-lead",
  "vendor_name": "João Silva"
}
```

---

## 🎯 Status dos Endpoints

1. ✅ Endpoint `/v1/brain` - Recebe mensagens do lead (IMPLEMENTADO)
2. ✅ Endpoint `/v1/vendor-message` - Recebe mensagens do vendedor (IMPLEMENTADO)
3. ⏳ Endpoint `/v1/history/{lead_id}` - Consultar histórico (OPCIONAL)
4. ⏳ Endpoint `/v1/leads` - Listar leads (OPCIONAL)

---

## 🔄 Integração com Make/Integromat

### Cenário 1: Mensagem do Lead
```
Uazapi Webhook → Make Trigger
  ↓
Make chama: POST /v1/brain
  ↓
API retorna: vendor_whatsapp, context, lead_whatsapp
  ↓
Make envia para vendedor via Uazapi
```

### Cenário 2: Mensagem do Vendedor
```
Uazapi Webhook (from vendor) → Make Trigger
  ↓
Make identifica que é vendedor
  ↓
Make chama: POST /v1/vendor-message
  ↓
API salva no histórico (direcao: 'out')
```

---

## 💡 Dicas

- Todas as mensagens são salvas no histórico
- A IA gera contexto apenas para novas mensagens do lead
- O vendedor sempre recebe o lead atribuído a ele
- O histórico permite rastrear toda a conversa
