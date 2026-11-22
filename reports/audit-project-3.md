# Relatório de auditoria — task-manager-api

**Data:** 2026-11-21
**Fase:** 2 — auditoria; nenhum arquivo da aplicação foi alterado
**Escopo examinado:** README, `requirements.txt`, `app.py`, `database.py`, `seed.py`, módulos `models/`, `routes/`, `services/` e `utils/` do repositório-base `mba-ia-refactor-projects-skill/task-manager-api`.

## Contexto do projeto

- **Domínio:** gerenciamento de tarefas, usuários, categorias, login e relatórios.
- **Linguagem/runtime:** Python; ambiente atual fornece 3.13.12. A versão-alvo do projeto não está fixada.
- **Framework/dependências:** Flask 3.0.0, Flask-SQLAlchemy 3.1.1, Flask-CORS 4.0.0, Marshmallow 3.20.1, Requests 2.31.0 e python-dotenv 1.0.0 em `requirements.txt`. Não há lockfile nem `node_modules`/ambiente local do projeto; a versão efetiva transitiva de SQLAlchemy não está registrada.
- **Persistência:** SQLite em `tasks.db` via Flask-SQLAlchemy; `db.create_all()` é executado ao importar/bootar `app.py`.
- **Comandos documentados:** `pip install -r requirements.txt`, `python seed.py`, `python app.py`. Não executados nesta Fase 1/2.
- **Inventário:** 15 módulos Python de aplicação: entrypoint e database, seed, 3 Models, 3 módulos de routes/Blueprints e respectivos `__init__`, service de notificações, helpers e seus `__init__`. Também foram inspecionados manifesto e README. Nenhum teste automatizado encontrado.
- **Arquitetura observada:** há Models, Blueprints/Routes, Services e Utils, porém a camada de rotas continua consultando/alterando ORM e executando regras diretamente. O service de notificação contém configuração sensível. A simples presença das pastas não caracteriza separação completa.
- **Superfícies revisadas:** configuração, boot, composição de Blueprints, autenticação/autorização, hash/serialização, operações CRUD, relatórios, consultas ORM, seed, tratamento de erros e utilitários.

## Endpoints e baseline

O código registra as rotas abaixo sem prefixos adicionais nos Blueprints (`app.py:18-20`). Status e corpos não foram exercitados nesta fase.

| Método | Caminho final | Handler/evidência | Baseline |
|---|---|---|---|
| GET | `/` | `app.py:26-28` | Estático; não executado |
| GET | `/health` | `app.py:22-24` | Estático; não executado |
| GET | `/tasks` | `routes/task_routes.py:11-12` | Estático; não executado |
| GET | `/tasks/<task_id>` | `routes/task_routes.py:65-66` | Estático; não executado |
| POST | `/tasks` | `routes/task_routes.py:85-86` | Estático; não executado |
| PUT | `/tasks/<task_id>` | `routes/task_routes.py:156-157` | Estático; não executado |
| DELETE | `/tasks/<task_id>` | `routes/task_routes.py:225-226` | Estático; não executado |
| GET | `/tasks/search` | `routes/task_routes.py:240-241` | Estático; não executado |
| GET | `/tasks/stats` | `routes/task_routes.py:273-274` | Estático; não executado |
| GET | `/users` | `routes/user_routes.py:10-11` | Estático; não executado |
| GET | `/users/<user_id>` | `routes/user_routes.py:27-28` | Estático; não executado |
| POST | `/users` | `routes/user_routes.py:42-43` | Estático; não executado |
| PUT | `/users/<user_id>` | `routes/user_routes.py:92-93` | Estático; não executado |
| DELETE | `/users/<user_id>` | `routes/user_routes.py:134-135` | Estático; não executado |
| GET | `/users/<user_id>/tasks` | `routes/user_routes.py:153-154` | Estático; não executado |
| POST | `/login` | `routes/user_routes.py:185-186` | Estático; não executado |
| GET | `/reports/summary` | `routes/report_routes.py:12-13` | Estático; não executado |
| GET | `/reports/user/<user_id>` | `routes/report_routes.py:103-104` | Estático; não executado |
| GET | `/categories` | `routes/report_routes.py:157-158` | Estático; não executado |
| POST | `/categories` | `routes/report_routes.py:167-168` | Estático; não executado |
| PUT | `/categories/<cat_id>` | `routes/report_routes.py:190-191` | Estático; não executado |
| DELETE | `/categories/<cat_id>` | `routes/report_routes.py:211-212` | Estático; não executado |

**Baseline de validação:** `python seed.py` apaga e recria os dados antes de `python app.py`; nenhum comando foi executado.
**Limitações:** fontes inspecionadas no repositório-base somente para leitura; versões efetivas não foram instaladas/confirmadas. Não há tests/OpenAPI/lockfile. Nenhum banco foi criado, seed executado ou endpoint chamado.

## Resumo por severidade

| CRITICAL | HIGH | MEDIUM | LOW | Total |
|---:|---:|---:|---:|---:|
| 2 | 1 | 5 | 3 | 11 |

## Achados

### [CRITICAL] Credenciais armazenadas com MD5 determinístico sem salt

- **Evidência:** `models/user.py:27-32`; `seed.py:16-35` cadastra usuários chamando `set_password` com senhas fracas de demonstração.
- **Condição/causa:** `set_password` e `check_password` aplicam MD5 simples e determinístico.
- **Impacto:** hashes são baratos de atacar e senhas iguais produzem o mesmo valor; vazamento do banco facilita recuperação de senhas.
- **Justificativa da severidade:** armazenamento de credencial com hash inadequado é risco grave, conforme escala do desafio.
- **Recomendação:** usar mecanismo de hash de senha apropriado com salt; migrar o formato no login bem-sucedido ou exigir redefinição para registros legados. Não expor valores em logs/relatório.
- **Confiança/limitação:** confirmado estaticamente; não foi feito ataque a hashes.

### [CRITICAL] Rotas sem autenticação permitem criar ou promover usuários a admin

- **Evidência:** `app.py:15-20` configura CORS e registra Blueprints sem middleware de autenticação; `routes/user_routes.py:42-78` aceita `role='admin'` diretamente no POST `/users`; `:92-125` permite alterar `role`/`active`; `:207-210` emite token literal previsível. Os handlers de escrita de tarefas/categorias também não verificam identidade/permissão.
- **Condição/causa:** a resposta de login contém string `fake-jwt-token-<id>`, mas não há validação de token nas rotas registradas; funções de criação/alteração aceitam role sem autorização.
- **Impacto:** qualquer cliente que alcance a API pode criar/promover uma conta privilegiada, alterar ou remover dados de outros usuários e operar tarefas/categorias sem autenticação.
- **Justificativa da severidade:** escalada de privilégio e escrita administrativa por rotas públicas afetam diretamente a segurança dos dados.
- **Recomendação:** emitir token assinado após login, validar sua assinatura/expiração nas rotas protegidas, aplicar autorização por proprietário/role e impedir que cadastro público escolha `admin`/`manager`.
- **Confiança/limitação:** ausência de middleware e verificações confirmada nos módulos de composição e handlers examinados; comportamento externo/deployment não foi avaliado.

### [HIGH] Chave Flask e credencial SMTP hardcoded com debug ativo

- **Evidência:** `app.py:11-13,33-34` fixa caminho do banco, `SECRET_KEY` e debug; `services/notification_service.py:7-10` contém host/usuário/senha SMTP.
- **Condição/causa:** segredos e opções de ambiente estão em código versionado; entrypoint inicia debug e escuta em `0.0.0.0`.
- **Impacto:** segredo pode ser reutilizado/extraído do repositório; debug em ambiente exposto pode revelar informação interna.
- **Justificativa da severidade:** configuração sensível hardcoded e debug ativo são risco relevante, conforme análise manual do desafio.
- **Recomendação:** carregar configuração sensível do ambiente/secret manager, validar no boot e manter debug desligado por padrão.
- **Confiança/limitação:** literals confirmados; não foi testada validade externa da credencial SMTP nem exposição do servidor.

### [MEDIUM] Serialização de usuário devolve o hash de senha

- **Evidência:** `models/user.py:16-25`, especialmente `:21`; o `to_dict()` é devolvido em `routes/user_routes.py:27-40,80-86,127-132,207-210`.
- **Condição/causa:** serialização genérica inclui o campo `password`, usado em respostas de consulta, criação, atualização e login.
- **Impacto:** clientes e sistemas intermediários recebem material de autenticação persistido.
- **Justificativa da severidade:** exposição de hash é séria, mas o finding é separado do método de armazenamento e limitado às respostas que usam `to_dict()`.
- **Recomendação:** serializer público por allowlist que nunca contenha senha/hash; manter campos públicos atuais.
- **Confiança/limitação:** confirmado estaticamente.

### [MEDIUM] Rotas executam consultas N+1 em tarefas, usuários e categorias

- **Evidência:** `routes/task_routes.py:14-16,41-57` percorre tarefas e busca User/Category para cada uma; `routes/user_routes.py:12-23` usa `len(u.tasks)` por usuário; `routes/report_routes.py:53-68` consulta tasks dentro do loop de usuários; `:159-165` conta tasks dentro do loop de categorias.
- **Condição/causa:** consultas dependentes são emitidas por linha/entidade em handlers.
- **Impacto:** round-trips ao banco crescem com o número de tarefas, usuários ou categorias e aumentam latência.
- **Justificativa da severidade:** padrão N+1 repetido nas listagens e relatórios e passível de agregação/eager loading.
- **Recomendação:** usar eager loading ou joins para relações e agregações agrupadas para contagens, preservando estruturas JSON.
- **Confiança/limitação:** confirmado estaticamente; sem benchmark.

### [MEDIUM] Listagens e relatórios carregam coleções completas em memória

- **Evidência:** `routes/task_routes.py:14,266,281` carrega todas as tasks em `/tasks`, busca e stats; `routes/report_routes.py:30-43,53-60` materializa todas as tasks e usuários no resumo antes de calcular contagens.
- **Condição/causa:** handlers usam `.all()` sem limite/paginação e iteram em Python para produzir resultados agregados.
- **Impacto:** memória e tempo de resposta crescem com a base; consultas em relatórios repetem o custo a cada request.
- **Justificativa da severidade:** gargalo de escala observável nos handlers e sem limites de conjunto.
- **Recomendação:** mover contagens/agrupamentos para SQL e definir paginação compatível com o contrato; documentar eventual mudança aditiva de resposta antes de alterar formato.
- **Confiança/limitação:** confirmado estaticamente; volume de produção desconhecido.

### [MEDIUM] Executar `seed.py` novamente apaga todos os registros existentes

- **Evidência:** `seed.py:8-14` exclui todas as tasks, users e categories antes de semear dados fixos; README instrui executar o seed antes do primeiro boot.
- **Condição/causa:** seed não verifica se o banco já foi populado nem separa carga inicial de reset explícito.
- **Impacto:** repetir o comando pode causar perda de dados operacionais; em produção o comando é destrutivo.
- **Justificativa da severidade:** risco de integridade e perda de dados provocado por comando documentado, embora dependa de execução manual.
- **Recomendação:** tornar seed idempotente (inserir somente o que falta) e reservar reset destrutivo para comando explícito de desenvolvimento.
- **Confiança/limitação:** confirmado no script; nenhum banco foi modificado.

### [MEDIUM] Endpoints de criação aceitam valores sem validação de tipo/limite consistente

- **Evidência:** `routes/task_routes.py:92-114,162-184` usa `len`, comparação numérica e membership sem validar que title/status/priority tenham tipos corretos; `routes/report_routes.py:196-202` acessa `data` sem tratar JSON ausente; `routes/user_routes.py:114-125` aplica `len`/atribuição direta para senha e active.
- **Condição/causa:** presença de JSON é validada em algumas rotas, mas tipos/limites não são normalizados uniformemente antes de regra e persistência.
- **Impacto:** payloads malformados podem resultar em 500, entrada inconsistente ou mudança de papel/estado.
- **Justificativa da severidade:** validação parcial afeta integridade e previsibilidade de endpoints de escrita.
- **Recomendação:** validar schemas e tipos na fronteira com mensagens/status compatíveis; testar payloads inválidos e não aplicar role/active sem autorização.
- **Confiança/limitação:** confirmado por inspeção; requests malformados não foram enviados.

### [LOW] Política de senha permite apenas quatro caracteres

- **Evidência:** `routes/user_routes.py:64-65,114-117`; constante correspondente em `utils/helpers.py:114`.
- **Condição/causa:** criação e atualização aceitam senha com quatro caracteres.
- **Impacto:** facilita credenciais fracas; risco é agravado pelo hash MD5 reportado separadamente.
- **Justificativa da severidade:** regra localizada de qualidade/segurança, classificada LOW conforme escala do desafio, sem minimizar a combinação com o finding CRITICAL.
- **Recomendação:** escolher e documentar política adequada e aplicá-la consistentemente em cadastro/atualização.
- **Confiança/limitação:** confirmado estaticamente.

### [LOW] `except:` genérico e imports mortos reduzem diagnóstico

- **Evidência:** `routes/task_routes.py:62-63,137-138,204-205,236-238`; `routes/user_routes.py:130-132,149-151`; `routes/report_routes.py:186-188,207-209,221-223`; imports sem uso observáveis em `app.py:7`, `routes/user_routes.py:6`, `routes/task_routes.py:7`, `routes/report_routes.py:8` e `utils/helpers.py:3-7`.
- **Condição/causa:** exceções amplas ocultam tipo/contexto de falha e módulos carregam imports mortos.
- **Impacto:** problemas de programação/infraestrutura ficam difíceis de diagnosticar; o ruído torna mudanças menos claras.
- **Justificativa da severidade:** melhoria localizada de manutenibilidade; exceções de persistência já fazem rollback em vários handlers.
- **Recomendação:** capturar exceções esperadas, registrar detalhes internamente sem dados sensíveis e remover imports sem uso.
- **Confiança/limitação:** confirmado estaticamente.

### [LOW] `Query.get()` está deprecated/legacy no SQLAlchemy permitido pela dependência

- **Evidência:** chamadas em `routes/task_routes.py:42,51,67,117,122,158,188,195,227`; `routes/user_routes.py:29,94,136,155`; `routes/report_routes.py:105,192,213`. `requirements.txt` fixa Flask-SQLAlchemy 3.1.1; o changelog oficial dessa versão define SQLAlchemy mínimo 2.0.16. A documentação oficial marca `Query.get()` deprecated desde SQLAlchemy 2.0 e informa a alternativa `Session.get()` ([Flask-SQLAlchemy 3.1.1 changes](https://flask-sqlalchemy.palletsprojects.com/en/stable/changes/); [SQLAlchemy Legacy Query API](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html)).
- **Condição/causa:** as chamadas `Model.query.get(id)` usam API de consulta legada.
- **Impacto:** warnings de depreciação e acoplamento ao estilo legado; sem versão resolvida não é possível afirmar comportamento específico do runtime instalado.
- **Justificativa da severidade:** dívida de compatibilidade localizada; API segue disponível como legado.
- **Recomendação:** migrar para `db.session.get(Model, id)` no contexto Flask-SQLAlchemy, compatível com a dependência declarada.
- **Confiança/limitação:** status de depreciação confirmado para a faixa permitida pela dependência; versão efetivamente instalada não confirmada por falta de lockfile/ambiente.

## Comparação com a análise manual

Os seis achados manuais foram confirmados: MD5 sem salt (CRITICAL), chave/SMTP/debug (HIGH), hash em resposta e consultas repetidas/carregamento integral (MEDIUM), senha mínima e exceções/imports (LOW). A auditoria separa o custo N+1 do carregamento integral e acrescenta ausência de autorização com possibilidade de criar/promover admin, seed destrutivo, validação incompleta e `Query.get()` legado para SQLAlchemy 2.x. Total: 11 findings.

## Escopo proposto para Fase 3

- **Correções de segurança/qualidade:** migrar MD5 gradualmente no login para KDF apropriado; excluir hash de toda resposta; mover chave/SMTP para ambiente e desativar debug por padrão; adicionar token assinado e autorização por identidade/role nas rotas privadas/escritas, com cadastro público incapaz de atribuir role privilegiada; revisar validação.
- **Ajustes arquiteturais:** preservar models/Blueprints/helpers úteis; extrair consultas e casos de uso que hoje vivem em routes para serviços/repositories coesos; corrigir N+1 com eager loading/agregações; tornar seed não destrutivo/idempotente; substituir `Query.get()` por `db.session.get()`.
- **Contratos públicos:** manter todos os 22 caminhos/métodos e estruturas JSON sempre que seguro. O `token` de login passará de literal fake a token assinado; rotas protegidas exigirão bearer token e cadastro público não poderá escolher role privilegiada. Essas mudanças de segurança alteram acesso/campos de autenticação e são explicitadas para aprovação. Nenhuma mudança de framework/ORM.
- **Validação planejada:** instalar versões de `requirements.txt`, executar seed em SQLite temporário, iniciar com debug desligado e exercitar todos os endpoints; validar login/token, autorizações, CRUD, relatórios e seed repetido. Comparar corpos/códigos quando possível; dados de senha/hash não devem aparecer em respostas.

## Gate de confirmação

Nenhum arquivo da aplicação foi alterado na Fase 1/2. **Você autoriza iniciar a Fase 3 no escopo acima, incluindo introduzir token assinado e autorização nas rotas, exigir token nas operações protegidas, impedir atribuição pública de role privilegiada e alterar o token retornado pelo login?** Aguardo confirmação explícita antes de criar ou alterar arquivos da aplicação.
