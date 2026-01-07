-- Script para popular dados de teste no banco
-- Execute este script no Supabase SQL Editor ou via cliente SQL

-- 1. Inserir Vendedores de Teste
INSERT INTO vendedores (nome, whatsapp_vendedor, ativo) VALUES
('João Silva', '5511999999999', true),
('Maria Santos', '5511888888888', true),
('Pedro Oliveira', '5511777777777', true),
('Ana Costa', '5511666666666', true)
ON CONFLICT DO NOTHING;

-- 2. (Opcional) Inserir alguns leads de teste já cadastrados
-- Descomente se quiser ter leads pré-cadastrados para teste
/*
INSERT INTO leads (whatsapp_lead, nome_ia, vendedor_id, status) 
SELECT 
    '5511970364501',
    'Lucas (Internet)',
    v.id,
    'novo'
FROM vendedores v 
WHERE v.nome = 'João Silva'
LIMIT 1
ON CONFLICT (whatsapp_lead) DO NOTHING;
*/

-- Verificar vendedores inseridos
SELECT id, nome, whatsapp_vendedor, ativo, created_at 
FROM vendedores 
ORDER BY created_at;
