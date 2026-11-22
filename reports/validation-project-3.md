# Evidência de validação — projeto 3 (`task-manager-api`)

Registro sanitizado da execução da Fase 3. Segredos e senhas de validação foram gerados/injetados apenas no processo e não aparecem neste artefato.

## Ambiente

- Dependências de `requirements.txt` instaladas isoladamente em `/tmp/task-manager-api-deps`; sem alterar o ambiente global ou manifesto.
- Resolução usada: Flask 3.0.0, Flask-SQLAlchemy 3.1.1 e SQLAlchemy 2.1.9.
- SQLite em arquivo temporário fora do repositório; `APP_SECRET_KEY`, senhas de seed, host e porta foram fornecidos pelo ambiente de execução.
- Servidor Flask vinculado somente a `127.0.0.1`; processo encerrado após as chamadas HTTP.

## Resultados observados

```text
python -m compileall: PASS
seed executado duas vezes no mesmo banco: PASS; contagens não duplicadas e dados não apagados
client Flask: PASS; as 22 rotas foram registradas e exercitadas
HTTP real com python app.py: PASS; boot e os 22 caminhos/métodos originais exercitados
rotas protegidas sem token: 401
token assinado adulterado: 401
usuário comum acessando dados/relatórios de outro usuário: 403
usuário comum promovendo papel ou alterando papel/estado: 403
cadastro legítimo: 201; tentativa de cadastro com role=admin: 403
respostas de usuário: sem campo password/hash
login de hash MD5 legado correto: sucesso e migração para scrypt
CRUD de tasks/users/categories e relatórios: respostas esperadas
```

As chamadas cobriram `GET /`, `GET /health`; todos os métodos de `/tasks`, `/users`, `/login`, `/reports` e `/categories` existentes no baseline. Os testes usaram dados de seed e um usuário temporário, removidos junto com o banco ao final. Nenhuma chamada a SMTP ou serviço externo foi feita.

## Limitações

- Não existe suíte automatizada no projeto-base; a verificação foi smoke/integration local executada com client Flask e HTTP.
- O banco legado existente não foi copiado nem migrado in place. Compatibilidade do hash foi validada em fixture MD5 temporária; a migração ocorre no primeiro login válido.
- Tokens dependem da `APP_SECRET_KEY`; em desenvolvimento sem variável configurada, a chave é aleatória por processo, então tokens deixam de valer ao reiniciar. Produção exige chave estável via ambiente/secret manager.
- Paginação não foi adicionada para preservar as estruturas de lista existentes; os N+1 foram reduzidos com eager loading e agregações SQL, mas listagens ainda podem carregar coleções grandes.
- SMTP permanece opcional e não foi exercitado; sem configuração, o serviço retorna falha controlada sem credenciais padrão.
