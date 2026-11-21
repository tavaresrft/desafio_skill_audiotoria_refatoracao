# Análise manual — code-smells-project

## Perfil e execução

- **Domínio:** API de e-commerce (produtos, usuários, pedidos e relatórios).
- **Stack:** Python 3 + Flask 3.1.1; `flask-cors` 5.0.1; SQLite via módulo padrão `sqlite3` (`requirements.txt`).
- **Inicialização:** `pip install -r requirements.txt && python app.py`; servidor em `0.0.0.0:5000`. `get_db()` inicializa o banco local `loja.db` no boot (`app.py:80-88`; README do projeto-base).
- **Persistência:** tabelas `produtos`, `usuarios`, `pedidos` e `itens_pedido`; conexão e criação das tabelas em `database.py`.
- **Fontes:** `app.py`, `controllers.py`, `models.py`, `database.py` (4 módulos Python da aplicação).
- **Arquitetura observada:** monólito funcionalmente dividido em módulos, mas sem separação efetiva de responsabilidades: rotas e operações administrativas em `app.py`, fluxo HTTP/validação em `controllers.py`, e funções chamadas de models contendo SQL e regra de negócio em `models.py`.

## Rotas confirmadas

`GET /produtos`, `GET /produtos/busca`, `GET /produtos/<id>`, `POST /produtos`, `PUT /produtos/<id>`, `DELETE /produtos/<id>`; `GET /usuarios`, `GET /usuarios/<id>`, `POST /usuarios`, `POST /login`; `POST /pedidos`, `GET /pedidos`, `GET /pedidos/usuario/<usuario_id>`, `PUT /pedidos/<pedido_id>/status`; `GET /relatorios/vendas`, `GET /health`, `GET /`, `POST /admin/reset-db`, `POST /admin/query` (`app.py:11-30,32-78`).

## Achados

### [CRITICAL] Endpoint administrativo executa SQL arbitrário

- **Evidência:** `code-smells-project/app.py:59-78`, em especial `:61-69`.
- **Problema:** `/admin/query` aceita `sql` do corpo HTTP e passa o texto diretamente a `cursor.execute(query)`.
- **Impacto:** um cliente que alcance a rota pode ler, alterar ou apagar os dados e executar operações destrutivas no banco. Não há autenticação/autorização visível na rota.
- **Justificativa:** execução de comando arbitrário e exposição da persistência atendem ao critério CRITICAL de segurança do desafio.

### [HIGH] Segredo hardcoded e exposto pela API

- **Evidência:** `code-smells-project/app.py:7-8` define chave e debug; `controllers.py:285-289` inclui `secret_key` na resposta de `/health` e declara `debug: True`.
- **Problema:** a chave está no fonte e é devolvida sem filtro em endpoint acessível; debug também é fixado ativo no boot (`app.py:88`).
- **Impacto:** clientes obtêm o segredo de sessão/configuração e detalhes de operação; configuração insegura pode habilitar exposição adicional em ambiente implantado.
- **Justificativa:** segredo embutido/publicado é risco direto e alta prioridade, mesmo que o projeto pareça didático.

### [MEDIUM] Injeção SQL nas operações do repositório

- **Evidência:** `code-smells-project/models.py:28`, `:47-50`, `:58-60`, `:92`, `:109-110`, `:126-129`.
- **Problema:** valores são concatenados às instruções SQL, inclusive email e senha no login. Há outras consultas montadas dinamicamente no mesmo arquivo (`:289-299`).
- **Impacto:** entradas com aspas ou conteúdo SQL podem alterar a consulta, contornar autenticação ou modificar registros; também causa falhas com dados legítimos contendo aspas.
- **Justificativa:** consultas parametrizadas são a fronteira básica entre dados e comandos SQL; o padrão aparece em vários fluxos, não em um caso isolado.

### [MEDIUM] Consultas repetidas por pedido (N+1)

- **Evidência:** `code-smells-project/models.py:174-200` e `:206-236`.
- **Problema:** para cada pedido, o código busca itens e, para cada item, busca o nome do produto com novas consultas.
- **Impacto:** o número de round trips cresce com pedidos e itens; listagens e relatórios ficam progressivamente mais lentos.
- **Justificativa:** consultas agregadas com `JOIN` ou carregamento em lote reduzem trabalho repetido e tornam o custo previsível.

### [LOW] Valores operacionais espalhados como literais

- **Evidência:** `code-smells-project/controllers.py:52-54,242-243`; `app.py:7-8,85-88`.
- **Problema:** listas de categorias e estados, versão/ambiente, porta e opções de debug estão embutidas nas rotas e entrypoint.
- **Impacto:** mudanças de regra exigem localizar e atualizar valores espalhados, com risco de inconsistência.
- **Justificativa:** constantes e configuração central melhoram leitura e manutenção; a severidade é baixa porque não interrompe o funcionamento por si só.

### [LOW] Controllers acumulam responsabilidades e respostas repetidas

- **Evidência:** `code-smells-project/controllers.py:5-12,24-62,188-220,264-292`.
- **Problema:** o módulo mistura validação, regra de fluxo, acesso direto ao banco em health check, logging por `print` e serialização HTTP; tratamento de erro se repete em handlers.
- **Impacto:** mudanças e testes ficam acoplados ao Flask e à persistência; inconsistências de resposta são mais prováveis.
- **Justificativa:** explicita a fronteira arquitetural que uma separação controller/service/repository poderia corrigir.

## Limites da análise

As evidências acima são estáticas, no código-fonte original. Não foram inferidos achados a partir de arquivos ausentes nem executados testes nesta etapa.

## Execução e refatoração — T5

### Resultado da auditoria

Relatório da Fase 2: [audit-project-1.md](../../reports/audit-project-1.md). Foram registrados oito findings: 3 CRITICAL, 1 HIGH, 2 MEDIUM e 2 LOW. Os seis achados manuais foram confirmados; a auditoria também encontrou senhas armazenadas/expostas em texto claro e `/admin/reset-db` sem autorização. As rotas administrativas de query e reset foram desativadas para impedir execução arbitrária de SQL e exclusão remota de todo o banco.

### Antes e depois

| Antes | Depois |
|---|---|
| Rotas e operações administrativas montadas no entrypoint | `app.py` como fábrica/composition root; `routes.py` registra Views/rotas |
| Controllers misturavam validação, acesso direto ao banco, respostas, logs e erros | Controllers coordenam HTTP; persistência fica em `models.py`; erros inesperados têm mapeamento central em `errors.py` |
| Conexão SQLite global compartilhada entre requests | Conexão no contexto Flask, fechada no teardown |
| SQL concatenava valores de entrada e pedidos faziam consultas aninhadas | Queries parametrizadas; pedidos usam leitura em lote com JOIN |
| Senhas em texto claro e respostas de usuário continham senha | Senhas com PBKDF2; senhas legadas são migradas no boot; JSON não inclui senha/hash |
| Chave/debug fixos; `/health` revelava chave e configuração local | Configuração por ambiente, debug desligado por padrão, health sanitizado |
| Endpoints `/admin/query` e `/admin/reset-db` executavam operações destrutivas | Ambos permanecem respondendo `410 Gone` sem executar a operação |

### Validação executada

- Dependências Flask 3.1.1 e flask-cors 5.0.1 instaladas em `/tmp/refactor-arch-deps`, sem alterar o manifesto do projeto.
- Boot real com `python app.py`, vinculado somente a `127.0.0.1`, com `DATABASE_PATH` apontando para banco temporário.
- **Resultado:** boot concluído; 19/19 endpoints originais receberam a resposta esperada. Foram exercitados CRUD de produto/usuário, login, criação/listagem/atualização de pedido, relatório e health. As duas rotas administrativas responderam `410` intencionalmente.
- **Segurança verificada:** respostas de `/usuarios` e `/usuarios/<id>` não contêm `senha`; a senha seed foi armazenada com prefixo PBKDF2 no banco temporário.
- **Isolamento:** testes usaram dados e banco sob diretório temporário; nenhuma operação destrutiva foi feita no banco do repositório-base.
- **Contrato:** métodos e caminhos foram mantidos. Há mudanças intencionais: campos de credencial e configuração removidos das respostas; endpoints administrativos desativados com `410`. Os demais formatos/códigos exercitados permaneceram compatíveis.
- **Limitações:** validação feita em ambiente local isolado e sem integração real de notificações; `/admin/reset-db` e `/admin/query` não foram executados além de confirmar o `410`.

### Comandos

```bash
cd code-smells-project
pip install -r requirements.txt
APP_SECRET_KEY="<valor-aleatorio>" python app.py
```

O teste de boot/HTTP foi feito com porta localhost e banco temporário, usando o mesmo entrypoint e os 19 caminhos mapeados no relatório. Os artefatos e código foram preparados neste repositório de entrega; ainda não há commit nesta etapa de registro.
