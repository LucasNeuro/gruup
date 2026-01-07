# 📊 Schema do Banco de Dados - CRM Brain

## Estrutura das Tabelas

### 1. **Tabela `vendedores`**
Armazena os vendedores que receberão os leads.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Chave primária (gerada automaticamente) |
| `created_at` | TIMESTAMP | Data de criação (UTC) |
| `nome` | TEXT | Nome do vendedor |
| `whatsapp_vendedor` | TEXT | Número do WhatsApp do vendedor |
| `ativo` | BOOLEAN | Se o vendedor está ativo (default: true) |

**Exemplo:**
```sql
INSERT INTO vendedores (nome, whatsapp_vendedor, ativo) 
VALUES ('João Silva', '5511999999999', true);
```

---

### 2. **Tabela `leads`**
Armazena os leads/clientes que entram em contato.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Chave primária (gerada automaticamente) |
| `created_at` | TIMESTAMP | Data de criação (UTC) |
| `whatsapp_lead` | TEXT | Número do WhatsApp do lead (UNIQUE) |
| `nome_ia` | TEXT | Nome gerado pela IA (ex: "Lucas (Internet)") |
| `vendedor_id` | UUID | Referência ao vendedor atribuído (FK) |
| `status` | TEXT | Status do lead (default: 'novo') |

**Exemplo:**
```sql
INSERT INTO leads (whatsapp_lead, nome_ia, vendedor_id, status) 
VALUES ('5511970364501', 'Lucas (Internet)', 'uuid-do-vendedor', 'novo');
```

---

### 3. **Tabela `historico_conversas`**
Armazena o histórico de todas as mensagens trocadas.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | UUID | Chave primária (gerada automaticamente) |
| `created_at` | TIMESTAMP | Data de criação (UTC) |
| `lead_id` | UUID | Referência ao lead (FK) |
| `direcao` | TEXT | 'in' (entrada) ou 'out' (saída) |
| `mensagem` | TEXT | Texto da mensagem |
| `resumo_ia` | TEXT | Resumo gerado pela IA (opcional) |

**Exemplo:**
```sql
INSERT INTO historico_conversas (lead_id, direcao, mensagem) 
VALUES ('uuid-do-lead', 'in', 'Preciso de uma internet pra minha residencia');
```

---

## 🔄 Relacionamentos

```
vendedores (1) ──< (N) leads (1) ──< (N) historico_conversas
```

- Um vendedor pode ter vários leads
- Um lead pode ter várias mensagens no histórico

---

## 🚀 Como Popular Dados de Teste

### Opção 1: Script SQL (Recomendado)
Execute o arquivo `populate_test_data.sql` no Supabase SQL Editor:

1. Acesse o Supabase Dashboard
2. Vá em **SQL Editor**
3. Cole o conteúdo de `populate_test_data.sql`
4. Execute

### Opção 2: Script Python
Execute via terminal:

```bash
python populate_test_data.py
```

Este script irá:
- ✅ Inserir 4 vendedores de teste
- ✅ Verificar se já existem antes de inserir
- ✅ Listar todos os vendedores cadastrados
- ✅ Opcionalmente criar um lead de teste

---

## 📝 Dados de Teste Incluídos

### Vendedores:
- João Silva - 5511999999999
- Maria Santos - 5511888888888
- Pedro Oliveira - 5511777777777
- Ana Costa - 5511666666666

**Nota:** Altere os números de WhatsApp para números reais quando for usar em produção!

---

## ✅ Verificações Úteis

### Ver todos os vendedores ativos:
```sql
SELECT * FROM vendedores WHERE ativo = true;
```

### Ver todos os leads:
```sql
SELECT l.*, v.nome as vendedor_nome 
FROM leads l 
LEFT JOIN vendedores v ON l.vendedor_id = v.id;
```

### Ver histórico de conversas de um lead:
```sql
SELECT * FROM historico_conversas 
WHERE lead_id = 'uuid-do-lead' 
ORDER BY created_at DESC;
```

---

## ⚠️ Importante

- O campo `whatsapp_lead` é **UNIQUE** - não pode haver duplicatas
- Use a **Service Role Key** do Supabase no backend (bypassa RLS)
- Os vendedores devem estar com `ativo = true` para receber leads
- O sistema atribui leads aleatoriamente entre vendedores ativos
