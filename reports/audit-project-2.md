# Relatório de auditoria — ecommerce-api-legacy

**Data:** 2026-11-21
**Fase:** 2 — auditoria; nenhum arquivo do projeto foi alterado
**Escopo examinado:** `package.json`, `package-lock.json`, `README.md`, `api.http` e os três fontes (`src/app.js`, `src/AppManager.js`, `src/utils.js`) do repositório-base `mba-ia-refactor-projects-skill/ecommerce-api-legacy`.

## Contexto do projeto

- **Domínio:** API de LMS com checkout, cursos, usuários, matrículas, pagamentos e relatório financeiro, conforme rotas, schema e exemplos HTTP.
- **Linguagem/runtime:** Node.js; disponível no ambiente como v22.21.0. Versão alvo do projeto não está declarada.
- **Framework/dependências:** Express range `^4.18.2` e sqlite3 `^5.1.6` em `package.json`; lockfile resolve Express 4.22.1 e sqlite3 5.1.7. `node_modules` não está presente.
- **Persistência:** SQLite `:memory:` criado em `AppManager` constructor; tabelas users, courses, enrollments, payments e audit_logs criadas/seedadas no boot.
- **Comando de inicialização disponível:** `npm install && npm start`, conforme README; `start` executa `node src/app.js`. Não executado nesta fase.
- **Arquitetura observada:** `src/app.js` configura Express e instancia `AppManager`; a classe concentra schema/seeds, acesso ao banco, rotas, checkout, relatório e exclusão; `src/utils.js` mistura configuração literal, cache global e função de hash.
- **Inventário:** 3 fontes JS, manifesto, lockfile, README e arquivo `.http`; nenhum teste automatizado ou diretório `node_modules` foi encontrado.
- **Superfícies revisadas:** configuração/segredos, checkout e cartão, senha/hash, queries, montagem de rotas, relatório, exclusão, callbacks/erros e exemplos de requisição.

## Endpoints e baseline

| Método | Caminho final | Handler/evidência | Baseline observado |
|---|---|---|---|
| POST | `/api/checkout` | `src/AppManager.js:28-78` | Estático; `.http` documenta payload de sucesso e recusa; não executado |
| GET | `/api/admin/financial-report` | `src/AppManager.js:80-129` | Estático; não executado |
| DELETE | `/api/users/:id` | `src/AppManager.js:131-137` | Estático; não executado |

**Comandos identificados:** `npm install` e `npm start`; scripts em `package.json` e README. Nenhum executado.
**Limitações:** análise estática dos fontes do repositório-base, fora do workspace gravável; versões de lockfile foram lidas, mas dependências não estão instaladas. Não foi feito checkout nem chamada HTTP. O pagamento mostrado é uma simulação local baseada em prefixo do cartão; não há gateway integrado no código observado.

## Resumo por severidade

| CRITICAL | HIGH | MEDIUM | LOW | Total |
|---:|---:|---:|---:|---:|
| 3 | 1 | 3 | 1 | 8 |

## Achados

### [CRITICAL] Credenciais ficam no fonte e dados de cartão são impressos em log

- **Evidência:** `src/utils.js:1-6` mantém valores de configuração com nomes de usuário/senha de banco, chave de pagamento e conta SMTP; `src/AppManager.js:43-46` imprime o cartão recebido e o valor de `paymentGatewayKey` durante checkout.
- **Condição/causa:** material de credencial está versionado e o PAN completo recebido no request é interpolado em `console.log`.
- **Impacto:** acesso ao repositório/log pode expor credenciais; logs retêm dados financeiros sensíveis. O conteúdo do campo com prefixo `pk_live_` é tratado como valor sensível pelo nome/uso, sem afirmar validade ou capacidade de cobrança externa.
- **Justificativa da severidade:** exposição de senha de banco e dados de cartão é risco grave, independente da validade externa da chave de pagamento.
- **Recomendação:** remover valores do código, obter configuração do ambiente, rotacionar credenciais expostas conforme aplicável e nunca registrar número de cartão ou segredo.
- **Confiança/limitação:** literals e interpolação confirmados no fonte; nenhum segredo foi copiado para este relatório e nenhuma credencial foi testada externamente.

### [CRITICAL] Hash de senha é determinístico, reversível na prática e usa senha padrão

- **Evidência:** `src/utils.js:17-23` repete prefixos de Base64 e retorna apenas dez caracteres; `src/AppManager.js:18` semeia usuário com senha em texto claro; `:66-70` usa `p || "123456"` e persiste o resultado de `badCrypto`.
- **Condição/causa:** função caseira não usa KDF nem salt; novo usuário pode ser criado sem `pwd`, recebendo senha previsível; seed persiste senha diretamente.
- **Impacto:** credenciais podem ser recuperadas ou adivinhadas com facilidade se o banco for obtido; senhas iguais geram material igual.
- **Justificativa da severidade:** armazenamento de autenticação gravemente inseguro e credencial padrão atendem ao critério CRITICAL.
- **Recomendação:** usar hash de senha com KDF/salt apoiado pela stack; exigir senha para conta nova e migrar seed/credenciais sem devolvê-las ou registrá-las.
- **Confiança/limitação:** confirmado estaticamente; o projeto não oferece endpoint de autenticação separado e o escopo exato de uso de `pass` além do checkout não está documentado.

### [CRITICAL] Qualquer cartão começando com `4` marca pagamento como pago sem processador

- **Evidência:** `src/AppManager.js:43-48` determina `status` exclusivamente por `cc.startsWith("4")`; `:50-60` cria matrícula e pagamento PAID depois dessa condição, sem chamada a gateway.
- **Condição/causa:** o dado controlado pelo cliente determina a aprovação; não há integração de pagamento no código examinado.
- **Impacto:** checkout pode emitir matrícula e registrar receita como paga sem autorização/transação financeira real.
- **Justificativa da severidade:** permite registrar acesso/receita sem confirmação de pagamento, afetando diretamente integridade financeira do fluxo.
- **Recomendação:** não tratar prefixo como autorização; encapsular provedor real ou simulação explícita de teste e só registrar PAID após confirmação de uma resposta verificável do provedor.
- **Confiança/limitação:** comportamento confirmado no código; nenhuma transação real foi tentada.

### [HIGH] `AppManager` concentra inicialização, persistência, rotas e casos de uso

- **Evidência:** `src/AppManager.js:4-23` inicializa banco/schema/seeds; `:25-78` declara checkout e persistência; `:80-129` agrega relatório; `:131-137` remove usuário e registra todas as rotas no mesmo objeto.
- **Condição/causa:** um único manager mistura composição HTTP, SQL, decisões de domínio, pagamento e resposta.
- **Impacto:** checkout/relatório dependem de estado e callbacks internos; alterações são difíceis de testar isoladamente e ampliam risco de efeitos cruzados.
- **Justificativa da severidade:** concentração de responsabilidades compromete substancialmente manutenção e testabilidade, em linha com HIGH do desafio.
- **Recomendação:** separar Router/Views, controllers, serviços de checkout/relatório, repository SQLite e inicialização/composição; manter camadas pequenas e explícitas.
- **Confiança/limitação:** confirmado pela estrutura integral do arquivo.

### [MEDIUM] Relatório financeiro executa padrão N+1 e não agrega no banco

- **Evidência:** `src/AppManager.js:83-127`; para cada curso busca matrículas (`:92`), para cada matrícula busca usuário e pagamento separadamente (`:104-106`).
- **Condição/causa:** loops aninhados disparam uma ou mais queries por curso/matrícula.
- **Impacto:** latência e número de operações crescem com cursos e matrículas; callbacks aninhados tornam falhas/ordenação mais difíceis de gerir.
- **Justificativa da severidade:** custo de leitura cresce com os dados e pode ser reduzido por join/agregação.
- **Recomendação:** uma consulta com joins/agregações ou carregamento em lote, preservando o array e os campos atuais do relatório.
- **Confiança/limitação:** confirmado estaticamente; desempenho não medido.

### [MEDIUM] Checkout aceita senha ausente e valores sem validação suficiente

- **Evidência:** `src/AppManager.js:28-36` exige `usr`, `eml`, `c_id`, `card`, mas não `pwd`; `:66-70` substitui senha ausente por default. Tipo/formato/limites de email, id e cartão também não são conferidos antes do fluxo.
- **Condição/causa:** validação limita-se à presença truthy de quatro campos e o campo de senha tem fallback previsível.
- **Impacto:** criação de usuário com credencial conhecida e entradas malformadas alcançam persistência/checkout.
- **Justificativa da severidade:** validação insuficiente na fronteira, com impacto direto em conta e pagamento simulado.
- **Recomendação:** validar tipo/formato/limites, exigir senha para novo usuário e preservar nomes dos campos e respostas para payloads válidos.
- **Confiança/limitação:** confirmado estaticamente.

### [MEDIUM] Exclusão deixa matrículas/pagamentos órfãos e responde sucesso mesmo após erro

- **Evidência:** `src/AppManager.js:12-16` cria tabelas sem chaves estrangeiras; `:131-136` apaga apenas `users` e ignora `err`, respondendo sempre texto de sucesso; a própria mensagem explicita que matrículas/pagamentos ficam no banco.
- **Condição/causa:** não há política de integridade/cascata nem verificação de erro da exclusão.
- **Impacto:** relatório mantém registros associados a usuário inexistente; resposta pode afirmar exclusão mesmo quando SQL falhou.
- **Justificativa da severidade:** produz estado inconsistente e sucesso falso em operação de escrita, acima de mero estilo.
- **Recomendação:** definir comportamento de integridade (transação/cascade ou regra explícita) e responder sucesso somente após confirmação da operação, mantendo o endpoint.
- **Confiança/limitação:** confirmado por schema, handler e mensagem estática.

### [LOW] Uso de mutabilidade e estado global sem necessidade clara

- **Evidência:** `src/AppManager.js:29-33,46,68,81-82` declara valores com `let` sem reatribuição; `src/utils.js:9-10,12-15` mantém cache/receita globais, mas `totalRevenue` não é usado e o cache não tem limite/escopo de lifecycle.
- **Condição/causa:** valores imutáveis são mutáveis e estado do processo é compartilhado entre requests.
- **Impacto:** reduz clareza e pode acumular/compartilhar estado inesperado conforme o processo roda.
- **Justificativa da severidade:** melhoria localizada de legibilidade/estado, sem falha funcional imediata comprovada.
- **Recomendação:** usar `const` e manter cache apenas se necessário, com escopo e política de expiração explícitos.
- **Confiança/limitação:** declarações e uso observáveis no fonte.

## APIs deprecated

Nenhuma API deprecated foi confirmada. Express e sqlite3 estão especificados e resolvidos no lockfile; não foi identificado uso com evidência de depreciação nos fontes. O ambiente não contém `node_modules`, portanto status baseado em warning de runtime não foi verificado.

## Comparação com a análise manual

Os seis achados manuais são confirmados: exposição de credenciais/cartão (CRITICAL), `AppManager` monolítico (HIGH), N+1 e validação/senha padrão (MEDIUM), mutabilidade local e erros não tratados (LOW). A auditoria separa armazenamento de senha fraco e aprovação fictícia de pagamento como riscos CRITICAL independentes, e detalha a exclusão que deixa registros órfãos. Total de oito findings.

## Escopo proposto para Fase 3

- **Correções de segurança/qualidade:** remover credenciais do fonte e PAN/chaves dos logs; substituir `badCrypto`/seed plaintext por KDF com salt e exigir senha; não marcar matrícula/pagamento como PAID com base no prefixo do cartão, deixando explícita qualquer simulação; validar campos obrigatórios; verificar erros e integridade na exclusão.
- **Ajustes arquiteturais:** separar Router/Views, controllers, serviços de checkout/relatório, repository e bootstrap; mover configuração a fonte de ambiente; reduzir N+1 e centralizar erros sem adicionar abstrações vazias.
- **Contratos públicos:** manter os três métodos/caminhos, nomes de entrada de checkout, texto/corpo e status de sucesso/recusa para fluxos válidos quando possível. Requisições sem senha que antes usavam default passarão a erro 400; resposta de erro para falhas de persistência será corrigida. Não serão feitas chamadas a gateway nem afirmado pagamento real; integração não existe no projeto.
- **Validação planejada:** instalar dependências via `npm install`, iniciar via `npm start`, exercitar checkout aceito/recusado, relatório financeiro e exclusão com dados isolados; comparar status/corpos com exemplos/documentação e registrar alterações intencionais. Dependências não instaladas e nenhuma validação foi executada até aqui.

## Gate de confirmação

Nenhum arquivo de aplicação foi alterado na Fase 1/2. **Você autoriza iniciar a Fase 3 neste escopo, incluindo remover segredos/logs de cartão, substituir o hash/senha padrão, não registrar pagamento como PAID pelo prefixo, e corrigir a exclusão de usuário para manter integridade e reportar falhas?** A autorização se limita às mudanças descritas acima. Aguardo confirmação explícita antes de criar ou alterar arquivos da aplicação.
