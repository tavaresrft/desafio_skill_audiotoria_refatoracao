# Relatório de auditoria — code-smells-project

**Data:** 2026-11-21
**Fase:** 2 — auditoria; nenhum arquivo do projeto foi alterado
**Escopo examinado:** quatro módulos da aplicação, manifesto de dependências e README do projeto-fonte `/home/romulo/projetos/full_cycle/mba-ia-refactor-projects-skill/code-smells-project`.

## Contexto do projeto

- **Domínio:** API de e-commerce para produtos, usuários, pedidos e relatório de vendas.
- **Linguagem/runtime:** Python; versão exata não declarada.
- **Framework/dependências:** Flask 3.1.1 e flask-cors 5.0.1 declarados em `requirements.txt`; ambiente instalado não confirmado.
- **Persistência:** SQLite via biblioteca padrão `sqlite3`; tabelas de produtos, usuários, pedidos e itens de pedido.
- **Comando de inicialização:** `pip install -r requirements.txt && python app.py`, conforme README. Não executado.
- **Arquitetura:** `app.py` compõe rotas e operações administrativas; `controllers.py` trata HTTP, validação, logs e exceções; `models.py` executa SQL, regras e serialização; `database.py` mantém conexão global, schema e seeds.
- **Inventário:** `app.py`, `controllers.py`, `models.py`, `database.py`, `requirements.txt` e README inspecionados; quatro módulos Python de aplicação.
- **Superfícies revisadas:** inicialização/configuração, rotas, endpoints administrativos, validação, SQL/persistência, serialização, pedidos/relatórios e erros.

## Endpoints e baseline

| Método | Caminho | Handler/evidência | Baseline |
|---|---|---|---|
| GET | `/produtos` | `app.py:11`, `controllers.py:5` | Estático; não executado |
| GET | `/produtos/busca` | `app.py:12`, `controllers.py:111` | Estático; não executado |
| GET | `/produtos/<id>` | `app.py:13`, `controllers.py:14` | Estático; não executado |
| POST | `/produtos` | `app.py:14`, `controllers.py:24` | Estático; não executado |
| PUT | `/produtos/<id>` | `app.py:15`, `controllers.py:64` | Estático; não executado |
| DELETE | `/produtos/<id>` | `app.py:16`, `controllers.py:98` | Estático; não executado |
| GET | `/usuarios` | `app.py:18`, `controllers.py:128` | Estático; não executado |
| GET | `/usuarios/<id>` | `app.py:19`, `controllers.py:136` | Estático; não executado |
| POST | `/usuarios` | `app.py:20`, `controllers.py:146` | Estático; não executado |
| POST | `/login` | `app.py:21`, `controllers.py:167` | Estático; não executado |
| POST | `/pedidos` | `app.py:23`, `controllers.py:188` | Estático; não executado |
| GET | `/pedidos` | `app.py:24`, `controllers.py:229` | Estático; não executado |
| GET | `/pedidos/usuario/<usuario_id>` | `app.py:25`, `controllers.py:222` | Estático; não executado |
| PUT | `/pedidos/<pedido_id>/status` | `app.py:26`, `controllers.py:237` | Estático; não executado |
| GET | `/relatorios/vendas` | `app.py:28`, `controllers.py:257` | Estático; não executado |
| GET | `/health` | `app.py:30`, `controllers.py:264` | Estático; não executado |
| GET | `/` | `app.py:32` | Estático; não executado |
| POST | `/admin/reset-db` | `app.py:47` | Estático; não executado |
| POST | `/admin/query` | `app.py:59` | Estático; não executado |

**Comandos identificados:** `pip install -r requirements.txt` e `python app.py`; nenhum executado. Status e corpos HTTP não foram observados. As fontes estão no repositório-base fora do workspace gravável; a pasta `code-smells-project/` deste workspace contém a skill, não a aplicação. Nenhum banco foi criado e nenhum endpoint foi chamado.

## Resumo por severidade

| CRITICAL | HIGH | MEDIUM | LOW | Total |
|---:|---:|---:|---:|---:|
| 3 | 1 | 2 | 2 | 8 |

## Achados

### [CRITICAL] Endpoint administrativo executa SQL arbitrário sem controle de acesso visível

- **Evidência:** `app.py:47-78`, especialmente `:59-78`. `/admin/query` lê o SQL enviado (`:61-64`) e chama `cursor.execute(query)` (`:66-69`); não há autorização no handler nem middleware de autorização visível na composição do app.
- **Condição/causa:** qualquer cliente que alcance a rota pode enviar SQL arbitrário; SELECT retorna linhas e outras operações são commitadas.
- **Impacto:** leitura, alteração ou exclusão arbitrária dos dados e exposição de erros do banco.
- **Justificativa:** execução arbitrária por entrada HTTP e ausência de controle de acesso observável atendem ao critério CRITICAL.
- **Recomendação:** remover execução genérica de SQL ou substituí-la por operações administrativas específicas e autorizadas.
- **Confiança/limitação:** confirmado estaticamente; nenhum request executado.

### [CRITICAL] Endpoint administrativo pode apagar todo o banco sem autorização visível

- **Evidência:** `app.py:47-57` registra `POST /admin/reset-db` e executa `DELETE` em itens, pedidos, produtos e usuários (`:49-55`); não há autenticação/autorização no handler nem middleware de autorização visível na composição do app.
- **Condição/causa:** cliente que alcance a rota pode apagar os dados persistidos com uma chamada.
- **Impacto:** perda integral e imediata dos dados da aplicação.
- **Justificativa da severidade:** operação destrutiva disponível por HTTP sem controle de acesso observável atende ao critério CRITICAL.
- **Recomendação:** remover/desativar a rota em runtime público ou torná-la uma operação restrita de manutenção, autorizada e executada apenas em ambiente isolado.
- **Confiança/limitação:** confirmado estaticamente; nenhum request destrutivo executado.

### [CRITICAL] Senhas em texto claro são persistidas e devolvidas por endpoints de usuário

- **Evidência:** `database.py:27-33,75-82` cria e semeia a coluna `senha`; `models.py:122-130` persiste a senha sem transformação; `models.py:72-87,89-103` inclui-a nos dicionários; `controllers.py:128-144` devolve esses dados em `/usuarios` e `/usuarios/<id>`.
- **Condição/causa:** credenciais são armazenadas em texto claro e incluídas nas respostas JSON de leitura.
- **Impacto:** vazamento da base expõe diretamente credenciais; clientes dos endpoints recebem senhas de usuários.
- **Justificativa:** exposição direta de credenciais persistidas é risco grave de segurança.
- **Recomendação:** não serializar credenciais e adotar hash de senha apropriado com migração segura dos registros existentes.
- **Confiança/limitação:** confirmado estaticamente; valores de exemplo foram omitidos.

### [HIGH] Chave Flask fixa é exposta em `/health` e debug fica habilitado

- **Evidência:** `app.py:6-8,80-88` configura chave e debug como valores fixos e inicia com `debug=True`; `controllers.py:276-290`, especialmente `:285-289`, devolve ambiente, caminho local, debug e chave.
- **Condição/causa:** configuração sensível no código aparece em endpoint acessível; debug ativo no entrypoint.
- **Impacto:** clientes obtêm a chave e detalhes operacionais; debug amplia exposição de diagnóstico fora do desenvolvimento.
- **Justificativa:** segredo hardcoded e publicado, associado a debug ativo, configura falha de alta prioridade.
- **Recomendação:** carregar segredos da configuração de ambiente, remover chave/detalhes desnecessários do health e desativar debug por padrão.
- **Confiança/limitação:** confirmado estaticamente; exposição externa não foi avaliada.

### [MEDIUM] Operações de persistência concatenam entrada em SQL

- **Evidência:** `models.py:24-29,43-50,54-61,65-69,105-111,122-130,285-300`; inclui login (`:109-110`) e busca (`:289-299`).
- **Condição/causa:** valores externos são incorporados ao SQL em vez de vinculados como parâmetros.
- **Impacto:** entradas com conteúdo SQL podem alterar consultas, contornar login ou modificar dados; caracteres legítimos também podem quebrar consultas.
- **Justificativa:** padrão repetido nas operações comuns, distinto do endpoint administrativo de SQL arbitrário.
- **Recomendação:** usar placeholders SQLite em todos os valores externos e bindings para filtros opcionais.
- **Confiança/limitação:** confirmado estaticamente; payloads não foram testados.

### [MEDIUM] Listagens de pedidos fazem consultas N+1

- **Evidência:** `models.py:171-200` e `:203-233`; cada pedido consulta itens (`:187-189`, `:219-221`) e cada item consulta produto (`:191-193`, `:223-225`).
- **Condição/causa:** queries aninhadas nos loops de pedidos e itens.
- **Impacto:** consultas e latência crescem com pedidos e itens em `/pedidos` e `/pedidos/usuario/<usuario_id>`.
- **Justificativa:** o custo cresce com volume e pode ser reduzido com consulta em lote/join.
- **Recomendação:** buscar itens e produtos em lote ou agregar via join, preservando resposta e ordenação.
- **Confiança/limitação:** confirmado estaticamente; desempenho não medido.

### [LOW] Regras e valores operacionais estão espalhados como literais

- **Evidência:** `controllers.py:52-54,242-243` define categorias e estados nos handlers; `app.py:7-8,80-88` fixa configuração, host, porta e debug.
- **Condição/causa:** regras e valores de execução ficam embutidos em pontos de controle/entrada.
- **Impacto:** mudanças exigem sincronizar valores espalhados, com risco de inconsistência.
- **Justificativa:** oportunidade localizada de manutenção, sem quebra funcional imediata demonstrada.
- **Recomendação:** centralizar configuração e constantes quando isso estabelecer uma fonte única útil.
- **Confiança/limitação:** confirmado estaticamente.

### [LOW] Controllers acumulam HTTP, regra, logging e acesso direto ao banco

- **Evidência:** `controllers.py:5-12,24-62,188-220,257-292`; mistura validação, coordenação, serialização, `print`, exceções e, no health check, conexão direta via `get_db()` (`:264-290`).
- **Condição/causa:** múltiplas responsabilidades e acoplamento entre Flask e persistência no módulo controller.
- **Impacto:** comportamento e falhas ficam mais difíceis de testar; tratamento HTTP repetido pode divergir.
- **Justificativa:** classificado LOW como oportunidade de manutenção/arquitetura, não falha funcional independente.
- **Recomendação:** manter handlers finos e extrair somente persistência/serviços com responsabilidade clara; centralizar erros se reduzir duplicação sem alterar respostas.
- **Confiança/limitação:** confirmado por inspeção; impacto em runtime não medido.

## APIs deprecated

Nenhuma API deprecated foi confirmada. Flask e flask-cors estão declarados, mas o ambiente instalado não foi verificado e não foi identificada chamada com evidência oficial de depreciação. Não se presume que APIs do Flask ou `sqlite3` estejam deprecated.

## Comparação com a análise manual

Os seis problemas previamente documentados foram confirmados com as mesmas severidades: SQL arbitrário (CRITICAL), segredo/debug (HIGH), SQL concatenado e N+1 (MEDIUM), literais e responsabilidades acumuladas (LOW). A auditoria acrescenta persistência e exposição de senhas em texto claro (`database.py`, `models.py`, `controllers.py`) e a operação destrutiva sem autorização em `/admin/reset-db`, não detalhadas na análise manual. Total: oito findings sustentados.

## Escopo proposto para Fase 3

- **Correções de segurança/qualidade:** desabilitar `/admin/query` e `/admin/reset-db` no runtime público; remover divulgação de chave/detalhes internos e desabilitar debug por padrão; corrigir armazenamento/serialização de credenciais com hash e respostas sem campo secreto; parametrizar SQL.
- **Ajustes arquiteturais:** extrair configuração de runtime; manter Models/persistência separados de HTTP; reduzir N+1; separar lógica operacional dos handlers somente onde houver benefício; centralizar erros onde compatível.
- **Contratos públicos:** preservar métodos/caminhos e formatos/códigos sempre que seguro. Remover `/admin/query` ou retirar campos secretos de respostas altera comportamento público por necessidade de segurança e está destacado para aprovação. Não ampliar mudanças incompatíveis.
- **Validação planejada:** boot segundo instruções/manifesto, testes disponíveis e exercício dos 19 endpoints acima; comparar status e formatos/campos quando possível. Usar banco e dados isolados; não chamar `/admin/reset-db`, operações de escrita ou `/admin/query` contra dados de produção. Validação ainda não executada.

## Gate de confirmação

Nenhum arquivo do projeto foi alterado nesta Fase 1/2. **Você autoriza iniciar a Fase 3 no escopo acima, incluindo desativar as rotas administrativas destrutivas, remover credenciais do JSON e migrar senhas para hash?** A confirmação se limita a esse escopo. Aguardo resposta afirmativa explícita antes de criar ou alterar arquivos do projeto.
