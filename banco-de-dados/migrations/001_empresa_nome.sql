-- Permite cadastrar empresas apenas com o nome, preservando dados existentes.
BEGIN;
ALTER TABLE empresa
    ALTER COLUMN razao_social DROP NOT NULL,
    ALTER COLUMN cnpj DROP NOT NULL,
    ALTER COLUMN cidade DROP NOT NULL;
COMMIT;
