# T4 — Registro de revisão da skill

## Escopo e método

Revisão estática de `docs/tasks/build.md`, do contrato T2 e de todos os arquivos da skill canônica. Verifiquei os critérios do desafio, observabilidade dos sinais, gates, cobertura das três combinações projeto/stack e igualdade das cópias. A revisão não executa/refatora os projetos; isso pertence às T5–T7 e depende da confirmação da Fase 2 da skill.

## Mapeamento dos requisitos

| Requisito do desafio | Local implementado | Resultado da revisão |
|---|---|---|
| Três fases sequenciais: análise, relatório/auditoria, refatoração | `SKILL.md` — Fluxo obrigatório | Atendido; fases 1 e 2 são somente leitura. |
| Heurísticas para linguagem, framework, banco, domínio, inventário e arquitetura | `references/project-analysis.md` — Descoberta sem pressupostos / stacks / rotas | Atendido; sinais são pontos de inspeção, não lista rígida de arquivos. |
| Catálogo com pelo menos oito padrões e severidades CRITICAL/HIGH/MEDIUM/LOW | `references/anti-pattern-catalog.md` | Atendido: 12 categorias, sinais, impacto e recomendação; severidades distribuídas e ajustáveis por consequência. |
| Deprecated API: confirmação da obsolescência e alternativa | `references/project-analysis.md` — Confirmação de APIs deprecated; catálogo item 12 | Atendido; versão/fontes oficiais exigidas, sem inventar versão ou substituto. |
| Template com contexto, achados e caminho/linha | `templates/audit-report.md` | Atendido; resumo por severidade, contexto, baseline, limitações, findings e gate; findings ordenados por severidade. |
| MVC e responsabilidades | `references/mvc-guidelines.md` | Atendido; Models/persistência, Views/Routes, Controllers/handlers e composição, com adaptações Flask/Express. |
| Pelo menos oito transformações antes/depois | `references/refactoring-playbook.md` | Atendido: 10 exemplos; Python/Flask, Node/Express e transformações conceituais aplicáveis a ambas. |
| Confirmação antes de qualquer modificação | `SKILL.md` — Fase 2; template — Gate de confirmação | Atendido; autorização após relatório e limitada ao escopo descrito. Pedido inicial/ambiguidade não libera escrita. |
| Preservar stack/contratos e adaptar-se ao projeto já organizado | `SKILL.md`; `references/mvc-guidelines.md` | Atendido; não migra stack, evita reestruturação estética e requer decisão para incompatibilidade. |
| Boot e endpoints originais, comparação de contrato/evidência | `SKILL.md` — Fase 3; `references/project-analysis.md` — Estratégia/checklist | Atendido; exige evidência e identifica como não verificado o que não foi executado. |
| Meta de pelo menos cinco achados em cada projeto, sem inventar | `SKILL.md` — Fase 2; catálogo; template | Atendido como meta de cobertura; se a inspeção ampla sustentar menos, explicar em vez de fabricar/duplicar. |
| Detecção correta de Flask em dois níveis de arquitetura e Express | `references/project-analysis.md`; `references/mvc-guidelines.md` | Atendido por detecção a partir de dependências/composição e arquitetura observada, não por domínio/nome de arquivo. |
| Configuração, modelos, rotas, controllers, erros e entrypoint no aceite de Fase 3 | `references/project-analysis.md` — Checklist adaptativo | Atendido; status aplicado/já atendido/não aplicável/pendente e sem camadas vazias. |

## Lacunas encontradas e correções

1. A skill não tornava explícita a meta de cinco findings nem o comportamento correto quando a varredura sustentasse menos. Incluí meta, varredura abrangente e proibição de completar contagem com especulação/duplicação.
2. A pergunta de confirmação podia ser interpretada como autorização ampla. Agora a confirmação se limita aos achados/mudanças enumerados no relatório; qualquer ampliação ou incompatibilidade exige nova decisão.
3. Faltava instrução explícita contra “zero problemas” sem varredura documentada e contra declarar ausência de problemas remanescentes após refatorar sem nova inspeção. Ambas foram adicionadas.
4. O checklist final de MVC/configuração/error handling do desafio não estava consolidado. Acrescentei avaliação adaptativa com estados e evidência, sem exigir camadas inúteis em projeto organizado.
5. Adicionei ordenação dos findings por severidade no template e na instrução operacional.

## Verificações

- O arquivo de entrada conserva `name: refactor-arch` e `SKILL.md`.
- Contagem conferida: 12 categorias de anti-pattern e 10 transformações numeradas antes/depois.
- As três pastas contêm a mesma estrutura e conteúdo, após propagar as correções da revisão.
- `git diff --check` executado sem erros.
- A revisão de T4 foi estática; não se alegou boot, testes ou endpoints validados nesta etapa.
