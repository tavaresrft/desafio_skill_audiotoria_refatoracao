# ecommerce-api-legacy

API de demonstração de LMS em Node.js/Express com checkout, SQLite, relatório financeiro e exclusão de usuário.

## Executar

```bash
npm ci
npm start
```

Por padrão, o serviço escuta em `0.0.0.0:3000` e usa SQLite em memória. `HOST`, `PORT` e `DATABASE_PATH` podem ser definidos no ambiente. O único modo de pagamento disponível é `PAYMENT_MODE=simulation`; o modo é sempre explícito no log de inicialização. Não há gateway conectado: o adaptador de demonstração aceita somente o cartão de teste listado em `api.http`, grava status `SIMULATED` e nunca representa uma cobrança real.

## Organização

- `src/app.js`: composition root, montagem Express, inicialização/encerramento.
- `src/config.js`: configuração por ambiente e validação do modo de pagamento.
- `src/routes/apiRoutes.js`: roteamento HTTP.
- `src/controllers/`: adaptação de request/response.
- `src/services/`: fluxo de checkout, senha e simulação de pagamento.
- `src/repositories/lmsRepository.js`: consultas e transações SQLite.
- `src/db/database.js`: schema, seeds, conexões e migração de senhas legadas.
- `src/middleware/errorHandler.js`: resposta central para erros inesperados.

## Endpoints

- `POST /api/checkout`
- `GET /api/admin/financial-report`
- `DELETE /api/users/:id`

Os caminhos e métodos foram mantidos. Novas contas precisam de senha com ao menos oito caracteres; checkout de conta existente verifica a senha. Campos e erros inválidos retornam 400/401. Exclusão remove matrículas e pagamentos relacionados em transação, retorna 404 para usuário inexistente e não reporta sucesso após falha.

## Smoke test

```bash
npm run test:smoke
```

O teste usa SQLite `:memory:` e porta local efêmera; cobre checkout aprovado/recusado/inválido, rejeição de cartão fora da simulação, relatório, scrypt e exclusão em cascata. Nenhuma chave, senha ou PAN é registrado em log.
