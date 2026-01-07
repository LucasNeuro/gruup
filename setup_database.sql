-- Create tables for CRM Brain MVP

-- 1. Tabela Vendedores
CREATE TABLE IF NOT EXISTS vendedores (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    nome TEXT NOT NULL,
    whatsapp_vendedor TEXT NOT NULL,
    ativo BOOLEAN DEFAULT TRUE
);

-- 2. Tabela Leads
CREATE TABLE IF NOT EXISTS leads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    whatsapp_lead TEXT NOT NULL UNIQUE,
    nome_ia TEXT,
    vendedor_id UUID REFERENCES vendedores(id),
    status TEXT DEFAULT 'novo'
);

-- 3. Tabela Histórico de Conversas
CREATE TABLE IF NOT EXISTS historico_conversas (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    lead_id UUID REFERENCES leads(id),
    direcao TEXT CHECK (direcao IN ('in', 'out')),
    mensagem TEXT,
    resumo_ia TEXT
);

-- Enable RLS (Optional but recommended, though we are using Service Role key in backend)
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE vendedores ENABLE ROW LEVEL SECURITY;
ALTER TABLE historico_conversas ENABLE ROW LEVEL SECURITY;

-- Create policies if needed (allowing public access for MVP simplicity if using anon key, but we have service role)
-- For now, we leave policies blank or open if using anon key. 
-- Assuming Service Role is used by the backend, it bypasses RLS.
