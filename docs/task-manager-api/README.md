# Análise manual — task-manager-api

## Perfil e execução

- **Domínio:** API de gerenciamento de tarefas, usuários, categorias e relatórios.
- **Stack:** Python + Flask 3.0.0, Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0, Marshmallow, Requests e python-dotenv (`requirements.txt`). Banco via SQLAlchemy/SQLite.
- **Inicialização:** `pip install -r requirements.txt && python seed.py && python app.py`; API em `0.0.0.0:5000`. O README-base recomenda executar seed antes do primeiro boot.
- **Persistência:** SQLite `tasks.db`; `db.create_all()` durante import/boot em contexto Flask (`app.py:30-31`). Entidades `User`, `Task`, `Category` em `models/`.
- **Fontes:** `app.py`, `database.py`, `seed.py`, `models/`, `routes/`, `services/`, `utils/`.
- **Arquitetura observada:** organização parcial por modelos, Blueprints, serviço de notificação e helpers, mas as rotas realizam consultas, regras de negócio e commits diretamente. `report_routes.py` também contém processamento agregado e cálculos.

## Endpoints confirmados

- Raiz e health: `GET /`, `GET /health` (`app.py:22-28`).
- Tarefas: Blueprint `task_bp` em `routes/task_routes.py`, com listagem, CRUD, busca e estatísticas.
- Usuários e login: Blueprint `user_bp` em `routes/user_routes.py`.
- Relatórios e categorias: Blueprint `report_bp` em `routes/report_routes.py`.
- Os prefixos/rotas são registrados diretamente sem prefixo de Blueprint em `app.py:18-20`.

## Achados

### [CRITICAL] Hash de senha usa MD5 sem salt

- **Evidência:** `task-manager-api/models/user.py:27-32`.
- **Problema:** `set_password` grava `hashlib.md5(...).hexdigest()` e `check_password` compara MD5 determinístico.
- **Impacto:** MD5 é rápido e sem salt, permitindo ataques de dicionário/rainbow table caso o banco seja exposto; senhas iguais produzem o mesmo hash.
- **Justificativa:** armazenamento de credencial com hash inadequado é falha grave de segurança.

### [HIGH] Segredo de aplicação hardcoded e debug habilitado

- **Evidência:** `task-manager-api/app.py:11-13,33-34`; adicionalmente `services/notification_service.py:7-10` contém host, usuário e senha SMTP no código.
- **Problema:** chave Flask e credencial SMTP estão fixas no fonte; servidor inicia em debug.
- **Impacto:** segredo de aplicação/SMTP pode ser extraído do repositório, e debug em ambiente exposto pode revelar informações internas.
- **Justificativa:** configuração sensível deve vir de ambiente/secret manager e debug não deve ser padrão de execução.

### [MEDIUM] Serialização de usuário inclui o hash da senha

- **Evidência:** `task-manager-api/models/user.py:16-25`, especialmente `:21`; uso da serialização nas respostas aparece em `routes/user_routes.py:85-86,128-129,207-210`.
- **Problema:** `to_dict()` devolve o campo `password`; rotas retornam esse dicionário ao criar/atualizar usuário e login.
- **Impacto:** clientes recebem material de autenticação persistido, que pode ser coletado em logs, caches ou dispositivos.
- **Justificativa:** campos sensíveis devem ser excluídos explicitamente de contratos de resposta, mesmo quando armazenados como hash.

### [MEDIUM] Relatórios fazem consultas repetidas e carregam coleções completas

- **Evidência:** `task-manager-api/routes/report_routes.py:30-35,53-60`; `routes/task_routes.py:14-16,281-287`.
- **Problema:** carrega todas as tasks para iterar em Python e faz consulta de tasks para cada usuário (`:53-60`), padrão N+1.
- **Impacto:** alto consumo de memória e consultas proporcionais ao número de usuários; o custo cresce com o conjunto de dados.
- **Justificativa:** agregações SQL, paginação e carregamento em lote mantêm latência/memória controláveis.

### [LOW] Política de senha permite credenciais muito curtas

- **Evidência:** `task-manager-api/routes/user_routes.py:64-65,114-117`.
- **Problema:** criação e atualização aceitam senha com apenas quatro caracteres.
- **Impacto:** senhas fracas tornam contas mais fáceis de comprometer, embora a correção principal esteja na política de autenticação/armazenamento.
- **Justificativa:** regra de validação claramente fraca e de correção localizada; classificada LOW dentro da escala de qualidade, sem minimizar o risco combinado com MD5.

### [LOW] Tratamento amplo de exceções e imports sem uso

- **Evidência:** `task-manager-api/routes/user_routes.py:6,130-132,149-151`; imports `hashlib` e `json` na linha 6 não são usados nesse módulo.
- **Problema:** blocos `except:` capturam qualquer exceção sem registrar causa nem tipo; imports mortos aumentam ruído.
- **Impacto:** erros de programação e infraestrutura ficam difíceis de diferenciar, e a manutenção exige mais investigação.
- **Justificativa:** é melhoria de legibilidade e diagnóstico; a análise não afirma que cada exceção capturada ocorra em produção.

## Limites da análise

A classificação sobre `Query.get()` como API deprecated não foi usada como achado nesta análise, pois exigiria confirmar comportamento da versão efetiva do ORM. Os achados listados são confirmáveis no código original; não foram executados testes nesta etapa.

## Auditoria, refatoração e validação — T7

O relatório da Fase 2 está em [audit-project-3.md](../../reports/audit-project-3.md). Ele registra 11 findings: 2 CRITICAL, 1 HIGH, 5 MEDIUM e 3 LOW. A auditoria confirmou os achados manuais e acrescentou, entre outros, ausência de autorização com promoção a admin, seed destrutivo, validação incompleta e uso da API legada `Query.get()`.

| Antes | Depois da T7 |
|---|---|
| Models, Blueprints/Routes, Services e Utils coexistiam, mas handlers ainda executavam regras e consultas ORM | Estrutura útil preservada; factory/composition root e `config.py`; routes atuam na fronteira HTTP e delegam casos de uso/consultas a Services; autorização por token e papel |
| MD5 e hash exposto em serialização; login devolvia token literal e rotas aceitavam mudanças de papel sem autorização | `scrypt` para novas senhas; hash MD5 é atualizado após login válido; respostas não incluem senha/hash; bearer tokens assinados e com expiração; acesso por usuário/papel; apenas admin altera papéis/estado e cadastro público não define role |
| Chave e SMTP no fonte; debug ativo; consultas repetidas e seed destrutivo | Segredo de aplicação obrigatório em produção e efêmero em desenvolvimento; SMTP configurado pelo ambiente; debug desligado; joins/agregações reduzem N+1; seed idempotente sem apagar registros |
| Validação de entrada e tratamento de erros inconsistentes; chamadas `Query.get()` | Validação de payloads fortalecida, erros de persistência registrados sem detalhes sensíveis na resposta e buscas por ID migradas para `db.session.get()` |

**Contratos:** os 22 caminhos e métodos originais foram preservados. Login agora retorna token assinado; operações protegidas exigem bearer token; dados de usuário não incluem senha; cadastro público não pode escolher papel; operações sobre recursos de outros usuários exigem papel apropriado. Essas mudanças de autorização e credenciais são intencionais e estão cobertas pela validação.

**Validação executada:** dependências pinadas instaladas isoladamente em `/tmp/task-manager-api-deps`; banco SQLite temporário em diretório descartável; seed executado duas vezes sem duplicar registros nem apagar conteúdo. Testes com client Flask e chamadas HTTP locais confirmaram boot e 22/22 caminhos/métodos, CRUD, login, permissões de usuário/admin, rejeição de token adulterado, respostas sem hash, migração de senha MD5 após login válido e códigos de erro esperados. O processo HTTP escutou somente em `127.0.0.1` e foi encerrado ao final. Evidência sanitizada: [validation-project-3.md](../../reports/validation-project-3.md).

**Como executar em ambiente local descartável:**

```bash
pip install -r requirements.txt
export APP_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DATABASE_PATH="/caminho/para/tasks-dev.sqlite"
export SEED_ADMIN_PASSWORD="<senha-local-com-8-ou-mais-caracteres>"
export SEED_DEMO_PASSWORD="<senha-local-com-8-ou-mais-caracteres>"
python seed.py
python app.py
```

Em produção, defina `APP_ENV=production` e forneça `APP_SECRET_KEY` por ambiente/secret manager; a aplicação falha no boot se a chave estiver ausente. O seed não apaga registros e só insere usuários/categorias/tasks que faltam; as senhas dos usuários seed vêm do ambiente e não são registradas. Contas existentes com MD5 são migradas no próximo login correto; recomenda-se que contas seed antigas troquem suas senhas fracas. SQLAlchemy não é pinado diretamente; a instalação validada resolveu SQLAlchemy 2.1.9 via Flask-SQLAlchemy 3.1.1.
