# Evidência de validação — projeto 2 (`ecommerce-api-legacy`)

Registro sanitizado da execução local feita durante a T6. Não contém credenciais, dados de cartão ou dados pessoais.

## Resultado observado

```text
npm ci: concluído; manifestos e lockfile não foram alterados
npm run test:smoke: PASS
  checkout aprovado/recusado/inválido: PASS
  cartão válido apenas pelo prefixo, conta recusada não criada: PASS
  relatório financeiro: PASS
  senha persistida com scrypt: PASS
  exclusão em cascata e resposta 404 para ID inexistente: PASS
node --check nos arquivos JavaScript: PASS
npm start (HOST=127.0.0.1, PORT=5183, DATABASE_PATH=:memory:): PASS
  POST /api/checkout: 200
  GET /api/admin/financial-report: 200
  DELETE /api/users/:id: 200
```

O processo local foi encerrado ao final da validação. A base SQLite em memória impediu uso de dados persistentes do repositório. Nenhum gateway de pagamento foi chamado; o resultado aprovado é explicitamente uma simulação. O registro de mudanças e limitações está no [README do projeto](../ecommerce-api-legacy/README.md) e no [relatório de auditoria](audit-project-2.md).

## Avisos de dependências

`npm ci` reportou 13 advisories: 2 low, 1 moderate, 8 high e 2 critical, além de avisos de dependências transitivas deprecated. A stack e o lockfile não foram atualizados nesta tarefa; os advisories requerem avaliação própria dos pacotes e caminhos afetados.
