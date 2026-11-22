# code-smells-project

API de e-commerce em Python/Flask com persistência SQLite.

## Executar localmente

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
APP_SECRET_KEY="<valor-aleatorio-local>" python app.py
```

O serviço escuta em `0.0.0.0:5000` por padrão. `HOST`, `PORT`, `FLASK_DEBUG`, `APP_SECRET_KEY` e `DATABASE_PATH` podem ser definidos pelo ambiente. Debug é desligado por padrão. Se `DATABASE_PATH` não for definido, o SQLite fica em `loja.db` ao lado da aplicação.

Na primeira inicialização, schema e dados demonstrativos são criados. A aplicação migra senhas legadas em texto claro para hashes PBKDF2 e novos cadastros são armazenados com hash. Os dados/contas de demonstração são apenas para desenvolvimento; substitua-os antes de qualquer uso real.

## Organização

- `config.py`: configuração externa e defaults seguros.
- `app.py`: fábrica da aplicação, composição e entry point.
- `routes.py`: registro dos endpoints HTTP (Views).
- `controllers.py`: validação e coordenação de casos de uso/serialização.
- `models.py`: consultas e operações de persistência SQLite parametrizadas.
- `database.py`: conexão por contexto Flask, schema, seeds e migração de credenciais legadas.
- `errors.py`: mapeamento central de falhas sem devolver detalhes internos.
- `security.py`: hash/verificação de senhas com biblioteca padrão.

## Endpoints administrativos

`POST /admin/query` e `POST /admin/reset-db` permanecem registrados para responder `410 Gone`, mas as operações arbitrárias/destrutivas estão desativadas. A resposta de `/health` não divulga segredo, caminho local nem modo debug. Os endpoints de usuário não serializam senha/hash.

## Validação

```bash
python app.py
```

O inventário de rotas está em [audit-project-1.md](../reports/audit-project-1.md); evidências de boot e endpoints estão em [validation-project-1.md](../reports/validation-project-1.md).
