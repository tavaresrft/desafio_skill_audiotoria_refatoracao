# Análise manual — ecommerce-api-legacy

## Perfil e execução

- **Domínio:** API de LMS com cursos, alunos, matrículas, pagamentos e checkout.
- **Stack:** Node.js + Express 4.18.2 + `sqlite3` 5.1.6 (`package.json`).
- **Inicialização:** `npm install && npm start`; o script executa `node src/app.js`, que escuta na porta configurada 3000. `AppManager` cria SQLite em memória e insere dados iniciais no boot (`src/AppManager.js:4-22`; README do projeto-base).
- **Persistência:** SQLite `:memory:` com tabelas users, courses, enrollments, payments e audit_logs (`src/AppManager.js:7,10-22`).
- **Fontes:** `src/app.js`, `src/AppManager.js`, `src/utils.js`; `api.http` contém exemplos de chamadas.
- **Arquitetura observada:** Express inicializa o processo, porém `AppManager` concentra inicialização de schema, rotas, SQL, validação e fluxo de pagamento. Não há diretórios separados para controllers, serviços ou acesso a dados.

## Endpoints confirmados

- `POST /api/checkout` — valida curso/usuário, registra matrícula e pagamento (`src/AppManager.js:28-78`).
- `GET /api/admin/financial-report` — relatório financeiro (`:80-129`).
- `DELETE /api/users/:id` — exclusão de usuário (`:131-137`).

## Achados

### [CRITICAL] Segredos de produção e dados de cartão são registrados em log

- **Evidência:** `ecommerce-api-legacy/src/utils.js:1-7` contém credenciais e chave `pk_live_...`; `src/AppManager.js:45` imprime o cartão recebido e a chave do gateway.
- **Problema:** segredo com aparência de credencial real está versionado, e dados de cartão são interpolados no log durante checkout.
- **Impacto:** qualquer pessoa com acesso ao código/log pode reutilizar a chave; logs podem reter dados de pagamento sensíveis. O uso do prefixo `pk_live_` é evidência literal do valor, não prova de validade externa.
- **Justificativa:** exposição de credenciais e dados financeiros é risco de severidade CRITICAL.

### [HIGH] AppManager é um objeto de responsabilidades excessivas

- **Evidência:** `ecommerce-api-legacy/src/AppManager.js:4-141`, sobretudo `:10-22` (schema/seeds) e `:25-137` (registro de rotas, regra e SQL).
- **Problema:** a mesma classe administra persistência, setup HTTP, checkout, relatório e deleção.
- **Impacto:** regras não são testáveis isoladamente, dependem de estado interno/Express/SQLite e mudanças em um fluxo ameaçam os demais.
- **Justificativa:** violação forte de separação de responsabilidades e alto acoplamento, conforme definição HIGH do desafio.

### [MEDIUM] Relatório financeiro usa padrão N+1 de consultas

- **Evidência:** `ecommerce-api-legacy/src/AppManager.js:83-127`, especialmente `:89-106`.
- **Problema:** para cada curso consulta matrículas e, para cada matrícula, faz consultas separadas de usuário e pagamento.
- **Impacto:** a quantidade de consultas cresce em proporção a cursos e matrículas; o relatório degrada com o volume e o código encadeado dificulta tratamento de erros.
- **Justificativa:** uma consulta com joins/agregação ou carregamento em lote reduz latência e complexidade.

### [MEDIUM] Checkout aceita campos incompletos e usa senha padrão

- **Evidência:** `ecommerce-api-legacy/src/AppManager.js:28-35,66-71`.
- **Problema:** valida `u`, `e`, `cid`, `cc`, mas não exige `pwd`; para novo usuário usa `p || "123456"`. Não há validação de formato de email/cartão ou tipo/limite dos campos.
- **Impacto:** cria contas com credencial previsível e faz validação insuficiente da entrada antes de executar uma operação de pagamento/matrícula.
- **Justificativa:** validações na borda são necessárias para integridade e segurança do fluxo.

### [LOW] Variáveis declaradas com `let` sem reatribuição

- **Evidência:** `ecommerce-api-legacy/src/AppManager.js:29-33,46,68,81-82`.
- **Problema:** diversos valores locais são declarados com `let` e nunca recebem outro valor (`u`, `e`, `p`, `cid`, `cc`, `status`, `hash`, `report`).
- **Impacto:** mutabilidade desnecessária amplia a superfície de erro e reduz clareza sobre quais valores realmente mudam.
- **Justificativa:** usar `const` onde aplicável é melhoria localizada de legibilidade, portanto LOW.

### [LOW] Erros de operações não são tratados de forma consistente

- **Evidência:** `ecommerce-api-legacy/src/AppManager.js:57-61,83-85,92-107,131-136`.
- **Problema:** callback de auditoria ignora `err`; o relatório não verifica erros em consultas internas e a exclusão responde sucesso mesmo se `db.run` falhar.
- **Impacto:** respostas podem indicar sucesso parcial ou ocultar falhas de banco, dificultando diagnóstico e deixando estado inconsistente.
- **Justificativa:** padronizar propagação de erro e respostas HTTP melhora confiabilidade sem exigir mudança de domínio.

## Limites da análise

A severidade CRITICAL para a chave é baseada no valor hardcoded e no nome de configuração `paymentGatewayKey`; não foi feita tentativa de validar a chave contra um serviço externo. Análise estática do código original; sem execução de testes nesta etapa.

## Execução e refatoração — T6

### Resultado da auditoria

Relatório da Fase 2: [audit-project-2.md](../../reports/audit-project-2.md). Foram registrados oito findings (3 CRITICAL, 1 HIGH, 3 MEDIUM, 1 LOW). Os seis achados manuais foram confirmados; a auditoria também detalhou a senha fraca/seed plaintext, a aprovação de pagamento baseada somente em prefixo e a exclusão que deixa matrículas/pagamentos órfãos.

### Antes e depois

| Antes | Depois |
|---|---|
| `AppManager` montava Express, schema/seeds, checkout, relatório e delete | `app.js` compõe; routes/views, controllers, services e repository têm responsabilidades separadas |
| Credenciais de banco/SMTP/pagamento no fonte; log imprimia cartão e chave | Valores removidos do fonte/log; checkout não persiste nem registra cartão |
| `badCrypto` repetia Base64 e usava senha padrão | `crypto.scrypt` com salt aleatório, comparação em tempo constante e migração de senhas legadas |
| Primeiro dígito do cartão marcava qualquer cartão iniciado por `4` como PAID | Adaptador de pagamento explicitamente simulado; cartão de teste aprovado limitado a valor exato e status persistido `SIMULATED` |
| Checkouts com callbacks aninhados e efeitos parciais | Serviço de checkout valida entrada e transação agrupa usuário, matrícula, pagamento simulado e audit log |
| Relatório consultava matrículas/usuário/pagamento repetidamente | Um JOIN monta os cursos, alunos e valores |
| Delete removia usuário apenas e sempre respondia sucesso | Exclusão transacional remove pagamentos/matrículas relacionados; checa erro e inexistência |

### Contratos e diferenças intencionais

Os três caminhos/métodos HTTP permanecem. O checkout de sucesso mantém o JSON `{ "msg": "Sucesso", "enrollment_id": ... }`, e recusa continua retornando 400. Senhas agora são obrigatórias para contas novas (mínimo oito caracteres), e contas existentes são autenticadas antes do checkout. O adaptador local aceita apenas cartão de teste aprovado/recusado e grava `SIMULATED`; não existe gateway nem cobrança. O seed de pagamento também é `SIMULATED`, então não aparece como receita paga no relatório. Delete retorna texto atualizado para refletir a remoção relacionada e 404 para ID inexistente. O exemplo `.http` de recusa foi atualizado para satisfazer a validação de senha.

### Validação executada

- `npm ci` instalou dependências do lockfile no workspace; manifestos/lockfile não foram atualizados.
- `npm run test:smoke` — **PASS**: checkout aprovado, recusado e inválido; cartão apenas com prefixo `4` recusado; nenhuma conta criada em checkout recusado; financial report; senha armazenada em scrypt; delete em cascata e 404.
- `npm start` com `HOST=127.0.0.1`, `PORT=5183` e `DATABASE_PATH=:memory:` — **PASS**: checkout HTTP 200, relatório HTTP 200, delete HTTP 200; processo e grupo de processos encerrados ao final.
- `node --check` nos arquivos JavaScript — **PASS**.
- `npm ci` reportou 13 advisories de dependências (2 low, 1 moderate, 8 high, 2 critical) e avisos de pacotes transitivos deprecated. Não atualizei a stack/lockfile nesta tarefa; a remediação desses advisories precisa de revisão específica dos pacotes/caminhos afetados.
- **Limitações:** pagamento continua uma simulação, não há integração externa. Registros `PAID` antigos gerados pela simulação anterior são migrados para `SIMULATED`; somente confirmação real poderá contar como receita paga. A rota de relatório `/api/admin/financial-report` não tinha mecanismo de autenticação no projeto-base e permanece sem ele para preservar o contrato existente; não exponha a API fora de um ambiente controlado até implementar autenticação/autorização administrativa. Não foi feita chamada a gateway.
