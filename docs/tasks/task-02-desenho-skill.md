# T2 — Contrato e desenho da skill

## Objetivo

Definir como a skill será executada, como separará conhecimento de instruções e como permanecerá reutilizável entre as três bases.

## Atividades

1. Confirmar a ferramenta agêntica e sua convenção para skills; manter o nome obrigatório `refactor-arch` e o arquivo `SKILL.md`.
2. Definir a localização canônica da skill em `code-smells-project/` e o procedimento para copiá-la integralmente aos outros dois projetos.
3. Especificar o fluxo estritamente sequencial: Fase 1 análise, Fase 2 auditoria e confirmação, Fase 3 refatoração e validação.
4. Definir os limites de escopo da refatoração: preservar contratos públicos, comportamento funcional e escolhas de stack, adaptando a arquitetura ao contexto encontrado.
5. Definir como serão resolvidos arquivos/linhas, severidade, APIs deprecated, endpoints de referência e comandos de validação.

## Critérios de aceite

- O desenho cobre Python/Flask e Node.js/Express sem regras dependentes de nomes ou arquivos exclusivos de um projeto.
- A skill não altera arquivos antes da confirmação explícita ao final da Fase 2.
- A Fase 3 prevê validação de inicialização e dos endpoints existentes, com evidências registradas.
- A arquitetura-alvo e a responsabilidade de Models, Views/Routes e Controllers estão descritas sem forçar reestruturação inútil em projeto já organizado.

## Checklist de conclusão

- [x] Ferramenta e convenção de skill definidas.
- [x] Localização canônica e estratégia de cópia definidas.
- [x] Fluxo das três fases e confirmação antes de alterações especificados.
- [x] Limites de escopo e preservação de contratos documentados.
- [x] Heurísticas para stack, severidade, linhas e validação definidas.
- [x] Arquitetura-alvo se adapta ao nível de organização de cada projeto.

Contrato detalhado: [Desenho da skill `refactor-arch`](task-02-desenho-skill-design.md).
