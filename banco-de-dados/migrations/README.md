Para bancos existentes, aplique a migração antes de usar o cadastro de empresa apenas com nome.
No PowerShell, a partir da raiz do projeto:

```powershell
Get-Content -Raw banco-de-dados/migrations/001_empresa_nome.sql | docker compose exec -T db psql -U postgres -d vagas_db -v ON_ERROR_STOP=1
```

A migração preserva os dados existentes e torna razão social, CNPJ e cidade opcionais.
Bancos novos já usam essas regras pelo arquivo `schema.sql`.
