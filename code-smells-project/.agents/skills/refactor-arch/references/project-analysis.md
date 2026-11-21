# Análise de projeto, evidências e validação

## Descoberta sem pressupostos

Trate os sinais abaixo como heurísticas. Descubra os arquivos reais por inventário; não exija nomes de arquivos, domínios, pastas ou modelos específicos.

1. **Linguagem e runtime:** extensões, manifestos, lockfiles, toolchain/configuração e comandos de execução. Exemplos: `pyproject.toml`, `requirements*.txt`, `package.json`, lockfiles, Dockerfile e CI.
2. **Framework e versões:** dependências/imports e pontos de inicialização/registro. Determine versões pelo lockfile, ambiente instalado ou manifesto aplicável; anote a fonte e divergências. Não inferir versões por sintaxe ou memória.
3. **Domínio:** nomes de entidades, operações, documentação e testes; descreva apenas o que a evidência sustenta.
4. **Persistência e integrações:** bibliotecas/clients, configuração, conexão, schema/migrations, modelos, consultas e limites externos. Nunca copie valores de credenciais para o relatório.
5. **Inicialização e validação:** README, scripts do manifesto, entrypoint, Docker/compose e CI. Extraia comandos existentes; distinguir comando recomendado de comando realmente executado.
6. **Inventário de código:** localizar entrypoints, rotas/handlers, validação, regras/casos de uso, persistência, middleware, serialização, configuração, testes e documentação. Informar arquivos examinados e lacunas relevantes.
7. **Arquitetura:** descrever fluxo observado de request até persistência e resposta. Registrar fronteiras e responsabilidades existentes antes de recomendar novas camadas.

## Como identificar stacks cobertas

- **Python/Flask:** dependências/imports Flask, construção de app, decorators de rota, Blueprints e registro de Blueprints. A aplicação pode usar views funcionais, extensões, serviços ou `sqlite3` sem ORM.
- **Node.js/Express:** `package.json`/lockfile, dependência/import Express, `express()`, `Router`, middlewares e registro/montagem de routers. A aplicação pode usar handlers funcionais, serviços e callbacks ou promises.
- Outros frameworks podem ser analisados com a mesma abordagem: localizar o mecanismo de entrada, composição de rotas, fluxo de dados e persistência sem presumir equivalência nominal de pastas.

## Rotas e contratos existentes

Construa a lista a partir de código efetivamente registrado: método, caminho final com prefixos, parâmetros, handler e middlewares relevantes. Cruze OpenAPI, testes, README e exemplos HTTP, registrando divergências; documentação isolada não comprova rota ativa. Inclua endpoints auxiliares/admin quando existirem. Não faça chamadas destrutivas/financeiras contra produção: prefira fixtures ou ambiente isolado.

Para baseline, registre respostas observadas de forma sanitizada: status, tipo/conteúdo estrutural, campos e efeitos esperados. Exclua tokens, senhas, dados pessoais e valores de pagamento. Se não for possível iniciar o serviço, registre o contrato estático e a limitação.

## Caminhos e linhas

- Cite caminhos relativos à raiz do projeto e números de linha atuais. Use `nl -ba` ou mecanismo equivalente para reabrir a região imediatamente antes de fechar o relatório.
- Use a linha exata da instrução e um intervalo curto quando necessário. Para causa e efeito distribuídos, cite definição e chamada/registro.
- Não propague números de uma análise antiga sem rever o conteúdo. Se a evidência não permitir precisão, declare isso; nunca fabrique linha.

## Severidade e findings

Use a escala do projeto e calibre pela consequência demonstrada, não apenas pelo nome do padrão:

- **CRITICAL:** exposição de segredos/dados sensíveis, execução arbitrária ou injeção explorável, armazenamento gravemente inseguro de credenciais, ou falha que inviabiliza operação segura/correta.
- **HIGH:** violação forte de responsabilidades/SOLID ou acoplamento que prejudica muito manutenção/testes; falha relevante de autorização/validação com impacto sustentado por evidência.
- **MEDIUM:** duplicação, N+1, validação incompleta ou padronização com impacto localizado em desempenho, integridade ou manutenção.
- **LOW:** legibilidade, imports mortos, mutabilidade local ou literais espalhados, sem impacto funcional/de segurança imediato demonstrado.

Cada finding descreve um problema independente, condição observada, evidência, impacto, justificativa da severidade e recomendação acionável. Evite duplicar o mesmo risco. Diferencie falha confirmada, hipótese e recomendação.

## Confirmação de APIs deprecated

Não declare API deprecated com base apenas em memória, warning genérico, sintaxe ou versão atual presumida.

1. Identifique chamada e pacote no código.
2. Confirme a versão efetiva por lockfile/ambiente; se impossível, declare a versão não confirmada.
3. Consulte documentação/notas oficiais do pacote para a versão relevante. Corrobore com warning de runtime, linter ou ferramenta da stack quando disponível.
4. Cite fonte, versão e data de consulta no relatório. Sem evidência suficiente, mantenha como “status não confirmado”, não como finding certo.
5. Recomende substituto apenas se a fonte oficial confirmar a alternativa para o contexto/versão. Não invente versão, prazo de remoção ou API; não atualize dependência sem autorização.

## Estratégia de validação pós-refatoração

Derive instalação, boot e testes dos manifestos/documentação/scripts presentes. Não substitua comandos do projeto por comandos presumidos. Depois da refatoração:

1. execute boot em ambiente isolado apropriado e registre comando, exit status e evidência de que ficou pronto;
2. execute a suíte pertinente existente;
3. exercite cada endpoint original descoberto, com dados seguros; compare status, campos e formato com baseline quando possível;
4. documente endpoints não exercitados, diferenças intencionais, falhas e limitações;
5. se algo não pôde ser executado, classifique como não verificado, nunca como aprovado.

## Checklist adaptativo de resultado

No relatório de conclusão da Fase 3, declare cada item como aplicado, já atendido, não aplicável ou pendente, com evidência breve:

- configuração separada de valores secretos/hardcoded e carregada de modo apropriado ao ambiente;
- persistência/Models com responsabilidades de dados claras;
- Views/Routes dedicadas a roteamento e adaptação HTTP;
- Controllers/handlers coordenando o fluxo sem acumular domínio ou SQL;
- tratamento de erro consistente/central quando a stack e aplicação comportarem essa fronteira;
- entrypoint/composition root claro;
- boot sem erro observado;
- endpoints originais respondendo conforme contrato, ou limitação registrada.

Não crie camada apenas para marcar item. Em um projeto organizado, “já atendido” é resultado válido; se algum item não se aplicar, justifique pela arquitetura e evidência.
