# Evidência de validação — projeto 1 (`code-smells-project`)

Registro sanitizado da execução local feita durante a T5. Não contém credenciais, valores de senha ou dados pessoais.

## Ambiente isolado

- Dependências Flask 3.1.1 e flask-cors 5.0.1 instaladas em `/tmp/refactor-arch-deps`, sem alterar o manifesto do projeto.
- Processo iniciado pelo entrypoint `python app.py`, ouvindo apenas em `127.0.0.1`.
- `DATABASE_PATH` apontado para SQLite temporário; nenhum banco persistente do repositório-base foi usado.

## Resultado observado

```text
boot: PASS
endpoints do baseline exercitados: 19/19 PASS
GET /health: 200; resposta sem chave secreta nem caminho local
GET /usuarios e GET /usuarios/<id>: sem campo senha/hash
senha de usuário seed no banco temporário: prefixo PBKDF2 verificado
POST /admin/query e POST /admin/reset-db: 410 Gone (desativados intencionalmente)
```

Foram exercitados CRUD de produtos e usuários, login, criação/listagem/atualização de pedido, relatório e health. Os 19 resultados incluem os dois `410` esperados para as rotas administrativas desativadas. O registro das mudanças está no [README do projeto](../code-smells-project/README.md) e no [relatório de auditoria](audit-project-1.md).

## Limitações

Execução local isolada; notificações externas não foram integradas. As rotas administrativas foram verificadas pelo retorno `410`, sem executar SQL arbitrário ou resetar banco.
