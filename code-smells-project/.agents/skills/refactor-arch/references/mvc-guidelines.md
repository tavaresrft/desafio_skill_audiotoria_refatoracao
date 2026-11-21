# Guidelines MVC adaptativas para APIs

MVC descreve responsabilidades, não uma árvore obrigatória nem nomes de classes. Primeiro mapeie o desenho existente e preserve qualquer separação que já funcione. Acrescente apenas a fronteira que resolve acoplamento demonstrado.

## Responsabilidades

- **Model/persistência:** entidades, mapeamento e operações de persistência. Em projetos simples pode ser um módulo de funções SQL; não precisa ORM. Não deve depender de `request`, `Response` ou formato HTTP.
- **View/Route:** entrada HTTP, roteamento, middleware e serialização da saída (JSON em APIs). Mantém validação de protocolo e delega o caso de uso; não concentra consultas/regras extensas.
- **Controller/handler:** coordena entrada, caso de uso e resultado HTTP. Pode ser função em Flask ou handler Express; não precisa classe. Evita SQL direto, integração externa e decisões de domínio extensas quando isso prejudica testes.
- **Serviço/caso de uso:** regra de domínio ou orquestração reutilizável. Não criar se o fluxo for trivial e já testável.
- **Composição/configuração:** app factory/entrypoint conecta routers, middleware, serviços e dependências; não é lugar para lógica de cada endpoint.

## Aplicação a Flask e Express

### Flask

Uma rota decorada pode atuar como view/controller fino. Blueprints agrupam rotas por coesão quando já úteis. Uma função de serviço pode receber valores explícitos, executar o caso de uso e retornar resultado independente de Flask; a persistência existente pode permanecer em SQL parametrizado ou ORM. Não exija `controllers/`, `views/` nem classes.

### Express

Um `Router` declara rotas/middleware; handler adapta request/response; serviço coordena domínio; repository/DAO encapsula acesso a dados se a separação trouxer benefício. Preserve callbacks/promises e tratamento de erro coerente com a versão/configuração existente. Não imponha classes ou pastas vazias.

## Regras de decisão

1. Preserve fronteiras já claras e testáveis.
2. Prefira extrair uma função coesa a criar várias camadas genéricas.
3. Passe dependências explicitamente apenas quando isso reduzir estado global ou facilitar teste; evite container/DI sofisticado sem necessidade.
4. Mantenha lógica de resposta/serialização no adaptador HTTP e domínio independente de status codes.
5. Não altere contrato por preferência de arquitetura. Se correção de segurança exigir incompatibilidade, exponha no relatório e peça decisão específica.
