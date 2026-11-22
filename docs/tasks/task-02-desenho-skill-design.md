# T2 — Contrato de execução da skill `refactor-arch`

Este documento fixa as decisões que a T3 deve implementar. A skill será escrita para Codex e manterá `SKILL.md` como arquivo de entrada obrigatório.

## Ferramenta, convenção e localização

- **Ferramenta agêntica:** OpenAI Codex, usando Agent Skills.
- **Convenção:** uma pasta por skill, com metadados `name` e `description` no front matter de `SKILL.md`; referências Markdown podem ficar em subpastas e ser lidas sob demanda.
- **Nome obrigatório:** `refactor-arch`.
- **Localização canônica:** `code-smells-project/.agents/skills/refactor-arch/`.
- **Cópias:** após concluir a skill canônica, copiar a pasta inteira, incluindo referências, templates e demais recursos, para `ecommerce-api-legacy/.agents/skills/refactor-arch/` e `task-manager-api/.agents/skills/refactor-arch/`. Não recriar arquivos manualmente nas cópias. Alterações posteriores devem ser feitas na canônica e propagadas às duas cópias; conferir igualdade recursiva dos arquivos e conteúdo antes de considerar a distribuição concluída. A única exceção é uma adaptação exigida pela ferramenta e documentada junto à cópia.
- **Invocação:** iniciar uma sessão Codex no diretório do projeto e pedir a execução de `refactor-arch`; a skill deve ser descoberta pelo diretório de skills do projeto.

## Fluxo obrigatório, estritamente sequencial

### Fase 1 — Análise

1. Inventariar o projeto sem modificá-lo: linguagem, runtime, framework, dependências e versões declaradas/instaladas, domínio, persistência, comandos de inicialização, arquivos-fonte, rotas/endpoints e organização atual.
2. Determinar a stack pela evidência do repositório (manifestos, imports, entrypoints e configuração), nunca pelo nome do projeto ou por uma lista fixa de arquivos.
3. Apresentar um resumo conciso e as fontes que sustentam a análise. Não propor nem aplicar mudanças nesta fase.

### Fase 2 — Auditoria e confirmação

1. Examinar padrões concretos e gerar relatório com achados individualizados, severidade, impacto, recomendação e evidência verificável de caminho e linha.
2. Identificar os endpoints originais e os comandos de validação que serão usados, indicando o que pôde ou não ser confirmado sem executar a aplicação.
3. Entregar o relatório completo para revisão humana e encerrar com uma pergunta explícita de confirmação para iniciar a Fase 3.
4. **Gate obrigatório:** não editar, criar, mover, remover, formatar ou aplicar correções em arquivos do projeto antes de confirmação explícita do usuário após apresentação do relatório. Silêncio, pedido de auditoria, execução da skill, confirmação implícita ou autorização anterior para analisar não contam como confirmação para refatorar. Se houver pedido de ajuste ao relatório, permanecer na Fase 2 e reapresentar o relatório atualizado antes do gate.

### Fase 3 — Refatoração e validação

Só iniciar depois da confirmação explícita. Aplicar mudanças em passos pequenos guiados por achados aprovados, preservar contratos públicos, comportamento funcional e stack, e adaptar a arquitetura ao estado observado. Evitar reestruturação por conformidade estética.

Validar a inicialização com o comando derivado das instruções e manifestos do projeto e exercitar todos os endpoints existentes identificados na Fase 1, por teste automatizado, cliente HTTP ou smoke test adequado. Comparar status, formato e campos das respostas com a referência anterior quando possível. Registrar comandos, resultados observados, endpoints cobertos, falhas, limitações e diferenças intencionais. Não declarar validação aprovada sem evidência observada; se a validação falhar, corrigir o que for necessário dentro do escopo confirmado e repetir as verificações afetadas.

## Limites de escopo e preservação

- Manter framework, linguagem, runtime e demais escolhas de stack. Uma atualização ou migração de stack exige motivo, análise de compatibilidade e autorização específica; não é subproduto de uma refatoração arquitetural.
- Preservar métodos/rotas públicas, verbos HTTP, caminhos, parâmetros, códigos de status, formatos/campos de resposta e efeitos funcionais existentes. Mudança de contrato necessária para corrigir risco deve ser destacada no relatório e aguardar decisão explícita; nunca introduzi-la silenciosamente.
- Priorizar correções de segurança e confiabilidade que preservem o contrato. Mitigar segredo exposto, SQL inseguro, dados sensíveis em logs e validação inadequada sem imprimir, copiar ou propagar valores sensíveis nos relatórios.
- Distinguir **correção de segurança/qualidade** de **recomendação arquitetural**. Aplicar mudanças de arquitetura apenas quando reduzirem acoplamento ou melhorarem teste/manutenção diante de evidência concreta. Não criar camadas, diretórios, interfaces ou abstrações sem responsabilidade real.
- Não ampliar o domínio nem reescrever comportamento sem achado correspondente e confirmação; manter mudanças rastreáveis aos itens aprovados.

## Arquitetura adaptativa e responsabilidades

Usar MVC como referência de responsabilidades, não como exigência de nomes ou diretórios. Primeiro descrever o que já existe. Se o projeto já tiver separação adequada, mantê-la e corrigir apenas lacunas. Se houver responsabilidades misturadas, extrair somente as fronteiras necessárias.

- **Models / persistência:** representam e persistem entidades; concentram mapeamento e operações de dados. Não devem formatar respostas HTTP nem depender do request/response do framework.
- **Views / Routes:** recebem a chamada HTTP, aplicam roteamento e serialização/formatos de resposta. Em API, a resposta JSON ocupa o papel de view; a camada não deve conter consultas extensas nem regra de domínio complexa.
- **Controllers:** coordenam o caso de uso, validam/normalizam entrada no limite apropriado e traduzem o resultado para a resposta HTTP. Regras de domínio complexas podem ficar em serviços/casos de uso existentes ou extraídos quando necessário.
- **Flask:** aceitar funções de view, Blueprints, serviços e repositórios já usados; não exigir classes Controller ou ORM se a aplicação usa `sqlite3` diretamente.
- **Express:** aceitar routers, handlers, serviços e DAOs/repositories idiomáticos; não impor classes ou camada de domínio sem benefício demonstrável.

## Heurísticas portáveis para a execução

### Stack, inventário e comandos

- Detectar Python/Flask por manifestos Python, dependências/imports Flask, criação da aplicação e registro de rotas; detectar Node/Express por `package.json`, dependência/import Express, criação do app/router e registro de rotas. Esses são sinais ilustrativos, não arquivos obrigatórios ou exclusivos.
- Procurar manifestos e lockfiles existentes para determinar dependências/versões. Registrar divergências entre declarado e instalado. Se a versão não puder ser confirmada, dizer isso em vez de inferir.
- Descobrir rotas em decorators/Blueprints, `app.route`, routers Express, middlewares e registro da aplicação; conferir documentação e exemplos HTTP sem presumir que estejam completos. Registrar método e caminho efetivamente montados, incluindo prefixos.
- Derivar comandos de instalação, boot e validação dos scripts, documentação e configuração existentes. Não inventar comandos ou dizer que um serviço iniciou sem executá-lo.

### Resolução de arquivo e linha

- Usar caminho relativo à raiz do projeto e números de linha atuais, obtidos no conteúdo em revisão. Preferir linhas exatas; usar intervalo pequeno quando a evidência ocupar várias linhas e apontar a instrução decisiva.
- Reabrir/contar as linhas imediatamente antes de emitir o relatório e após alterações. Não reaproveitar números de análises antigas sem conferir o estado atual.
- Para achado distribuído, listar cada local relevante; para comportamento que dependa de chamada, citar tanto a definição quanto o uso. Se o arquivo ou linha não puder ser determinado, declarar a limitação e não fabricar precisão.

### Severidade

Aplicar a escala do desafio de acordo com consequência e evidência, não com o rótulo do anti-pattern:

- **CRITICAL:** exposição grave de segredo/dado sensível, execução arbitrária/injeção explorável, credencial fraca armazenada de forma insegura ou falha arquitetural que inviabiliza operação segura/correta.
- **HIGH:** acoplamento ou violação forte de responsabilidades/SOLID que compromete manutenção e testes; validação/autorização ausente com impacto relevante.
- **MEDIUM:** duplicação, N+1, validação incompleta ou problema de padronização com impacto localizado em desempenho, integridade ou manutenção.
- **LOW:** legibilidade, imports mortos, mutabilidade local, literais e melhorias localizadas sem impacto funcional ou de segurança imediato.

Cada finding contém **um problema**, evidência, condição observada, impacto, justificativa da severidade e recomendação. Evitar duplicar o mesmo risco em vários findings; separar causas independentes mesmo que estejam no mesmo arquivo.

### APIs deprecated

- Não classificar uma API como deprecated apenas por memória, nome parecido ou versão atual presumida.
- Confirmar primeiro a versão efetivamente usada por manifestos/lockfile ou ambiente e localizar a chamada concreta. Procurar aviso/documentação oficial da biblioteca para aquela versão; quando disponível, corroborar com aviso de runtime, lint ou mecanismo de depreciação da própria stack.
- Registrar API, pacote e versão confirmados, evidência e referência consultada/data. Se a versão ou status não puder ser confirmado, marcar como hipótese pendente, sem declarar deprecated nem prescrever substituto como fato.
- Recomendar alternativa somente quando a fonte oficial ou a documentação da versão suportar a substituição; não inventar versão, data de remoção ou API substituta. Não atualizar dependência automaticamente sem autorização.

### Endpoints e referências de contrato

- Montar inventário a partir da composição real da aplicação: método, caminho final, parâmetros e handler, incluindo prefixos/middlewares de registro.
- Cruzar fontes (código, testes, OpenAPI, README, coleção `.http`) e marcar divergências; código registrado em runtime é referência primária do endpoint existente.
- Usar testes e respostas observadas como referência de contrato. Quando não houver teste/execução possível, registrar a fonte estática e a incerteza. Após refatorar, cobrir cada endpoint original, inclusive health/admin quando existente e acessível; para rotas destrutivas ou com efeitos financeiros, usar ambiente e dados isolados seguros.

### Validação e evidências

- Antes de alterar, registrar o baseline verificável: comandos disponíveis, endpoints, status/campos conhecidos e limitações.
- Após mudança, executar boot e os testes existentes pertinentes, mais smoke tests de cada endpoint original. Comparar contratos/respostas quando possível sem depender de valores voláteis; não registrar segredos nem dados pessoais nas evidências.
- Relatar para cada comando: comando exato, resultado/exit status, escopo coberto e limitações. Distinguir teste executado, inspeção estática e comportamento não verificado.

## Entregáveis previstos para a T3

A pasta de skill deve conter `SKILL.md` conciso, mais referências Markdown separadas para análise de projeto, catálogo de anti-patterns, template do relatório da Fase 2, guidelines MVC e playbook de transformações. Instruções operacionais ficam no `SKILL.md`; conhecimento detalhado fica nas referências. A T3 deve incluir exemplos aplicáveis a Flask e Express sem acoplar a regras a nomes de arquivos, domínios ou modelos exclusivos destes três projetos.
