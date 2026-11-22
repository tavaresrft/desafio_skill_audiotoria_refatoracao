# Task Manager API

API de tarefas em Python/Flask, refatorada como parte do desafio `refactor-arch`. As camadas úteis de Models, Routes, Services e Utils foram preservadas; a aplicação usa uma factory como composition root, configurações isoladas em `config.py`, e Routes delegam casos de uso às Services.

## Executar localmente

Use Python compatível com `requirements.txt` e um banco descartável. Defina `APP_SECRET_KEY`, `DATABASE_PATH`, `SEED_ADMIN_PASSWORD` e `SEED_DEMO_PASSWORD` no ambiente antes de executar `seed.py`. As duas senhas do seed precisam ter no mínimo oito caracteres. O seed é idempotente e não remove dados. Em produção, `APP_SECRET_KEY` é obrigatória e deve vir de um secret manager.

```bash
pip install -r requirements.txt
export APP_SECRET_KEY="<segredo-aleatorio-fornecido-pelo-ambiente>"
export DATABASE_PATH="/caminho/para/tasks-dev.sqlite"
export SEED_ADMIN_PASSWORD="<senha-local-forte>"
export SEED_DEMO_PASSWORD="<senha-local-forte>"
python seed.py
python app.py
```

O servidor usa `127.0.0.1:5000` por padrão; `HOST` e `PORT` podem ser configurados no ambiente. SMTP é opcional e usa `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER` e `SMTP_PASSWORD`.

## Autenticação e autorização

`POST /login` emite bearer token assinado, com expiração configurável por `TOKEN_TTL_SECONDS` (padrão de uma hora). Cadastro público cria apenas usuários comuns. Rotas de tarefas exigem token e limitam usuários comuns às próprias tasks; operações administrativas e relatórios gerais exigem papel apropriado. Apenas admins podem alterar papel/estado ou remover usuários. Respostas públicas nunca incluem senha/hash.

Novas senhas usam scrypt. Um hash MD5 legado é migrado para scrypt após autenticação correta. Contas de seeds antigos devem trocar qualquer senha fraca. A lista baseline dos 22 endpoints está em [reports/audit-project-3.md](../reports/audit-project-3.md), com evidências da validação em [reports/validation-project-3.md](../reports/validation-project-3.md).
