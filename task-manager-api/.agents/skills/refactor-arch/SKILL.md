---
name: refactor-arch
description: Audita e refatora APIs ou aplicações para responsabilidades MVC adequadas à stack existente. Executa análise, auditoria e confirmação humana antes de qualquer alteração, depois refatora e valida inicialização e contratos existentes.
---

# refactor-arch

Conduza uma auditoria e, somente após autorização explícita, uma refatoração arquitetural adaptada ao projeto. Preserve linguagem, framework, comportamento e contratos públicos. Não force MVC nominalmente quando a estrutura atual já separa bem as responsabilidades.

## Fluxo obrigatório

Execute as três fases na ordem. Não avance além da Fase 2 sem uma resposta afirmativa explícita posterior ao relatório.

### Fase 1 — Análise (somente leitura)

Inspecione os manifestos, código, testes, documentação e configuração disponíveis para identificar linguagem/runtime, framework e versões confirmáveis, domínio, persistência, comandos, arquitetura, arquivos relevantes e inventário de endpoints. Siga `references/project-analysis.md`. Apresente o resumo e as fontes. Não altere arquivos.

### Fase 2 — Auditoria e confirmação (somente leitura)

Identifique problemas concretos, com severidade, impacto, justificativa, recomendação e caminho/linha atual. Ordene os findings de CRITICAL a LOW. Use `references/anti-pattern-catalog.md`; os exemplos são heurísticas, não achados sem evidência. Verifique APIs supostamente deprecated conforme o procedimento da referência. Gere o relatório usando `templates/audit-report.md`, incluindo baseline de boot/endpoints e limitações.

Faça uma varredura suficientemente ampla para atender ao critério do desafio de pelo menos cinco findings por projeto, incluindo ao menos um CRITICAL ou HIGH quando houver evidência. Não complete contagem com achados especulativos ou duplicados: se, após revisar as áreas relevantes, houver menos de cinco problemas sustentáveis, registre as áreas examinadas, explique a contagem menor e não invente problemas. Só reporte “nenhum achado” após examinar e documentar as áreas pertinentes; silêncio do catálogo ou busca parcial não prova ausência.

Apresente o relatório completo e pergunte claramente se o usuário autoriza iniciar a Fase 3 para o escopo enumerado em “Escopo proposto”. **Até receber confirmação afirmativa explícita após esse relatório, não crie, altere, mova, remova ou formate nenhum arquivo do projeto.** A solicitação inicial para auditar ou executar esta skill não autoriza a refatoração. A confirmação só cobre achados e mudanças descritos no relatório; não autoriza expandir o escopo, alterar contratos públicos ou trocar stack. Se o usuário pedir mudanças no relatório, permaneça nesta fase, atualize-o e solicite confirmação novamente. Respostas ambíguas não liberam o gate.

### Fase 3 — Refatoração e validação

Somente após a confirmação: aplique os achados aprovados em mudanças pequenas e rastreáveis; use `references/mvc-guidelines.md` e `references/refactoring-playbook.md`. Avalie configuração segura, persistência/Models, Views/Routes, Controllers/handlers, tratamento central de erros e entrypoint conforme as necessidades observadas; crie/separe esses papéis quando reduzirem um problema evidenciado, sem diretórios ou camadas vazias. Separe correções necessárias de segurança/qualidade de recomendações arquiteturais. Preserve contratos e comportamento; uma mudança incompatível exige decisão específica. Não atualize stack nem invente APIs substitutas.

Valide a inicialização e todos os endpoints originais encontrados na Fase 1 com comandos derivados do projeto. Execute testes disponíveis, compare status, formato e campos com o baseline quando possível e registre evidências, comandos, resultados, limitações e diferenças intencionais. Faça nova varredura dos mesmos sinais após a mudança e reporte findings resolvidos, pendentes ou aceitos; só declare ausência de problemas remanescentes se registrar o escopo efetivamente revisto. Não declare sucesso para verificações não executadas. Veja `references/project-analysis.md` para registro de evidências.

## Referências

- Análise e validação: `references/project-analysis.md`
- Catálogo e severidade: `references/anti-pattern-catalog.md`
- Contrato do relatório: `templates/audit-report.md`
- Responsabilidades MVC: `references/mvc-guidelines.md`
- Transformações concretas: `references/refactoring-playbook.md`
