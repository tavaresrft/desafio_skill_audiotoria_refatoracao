# Plano de tarefas — Refatoração arquitetural automatizada

As tarefas abaixo decompõem o desafio descrito em [`build.md`](build.md). Execute na ordem indicada; tarefas independentes dentro da mesma etapa podem ser feitas em paralelo.

## Pré-requisito

O workspace de documentação mantém os registros em `docs/<nome-do-projeto>/README.md`; os fontes originais ficam no repositório base. Antes das tarefas de execução (T5–T7), disponibilize os projetos-alvo em um local acessível e configure a ferramenta de agente escolhida. Atualize o README correspondente em `docs/` ao concluir cada etapa do projeto.

## Sequência

| ID | Tarefa | Depende de |
| --- | --- | --- |
| T1 | Inspecionar os três projetos e registrar a análise manual | Pré-requisito |
| T2 | Definir contrato, estrutura e regras da skill | T1 |
| T3 | Criar `SKILL.md` e referências | T2 |
| T4 | Revisar a skill contra cobertura e portabilidade | T3 |
| T5 | Executar e refatorar o projeto 1 | T4 |
| T6 | Executar e refatorar o projeto 2 | T4 |
| T7 | Executar e refatorar o projeto 3 | T4 |
| T8 | Consolidar resultados, README e artefatos | T5, T6, T7 |
| T9 | Revisão final do entregável | T8 |

## Documentação por projeto

- `docs/code-smells-project/README.md`: análise manual e execução/refatoração do projeto 1.
- `docs/ecommerce-api-legacy/README.md`: análise manual e execução/refatoração do projeto 2.
- `docs/task-manager-api/README.md`: análise manual e execução/refatoração do projeto 3.

As tarefas T5–T7 devem acrescentar ao README correspondente os resultados reais da skill, mudanças aplicadas, validação e limitações. A T8 consolida esses registros e confere consistência com o README raiz e relatórios.

## Tarefas detalhadas

- [T1 — Análise manual](task-01-analise-manual.md)
- [T2 — Contrato e desenho da skill](task-02-desenho-skill.md)
- [T3 — Implementação da skill](task-03-implementacao-skill.md)
- [T4 — Revisão de cobertura e portabilidade](task-04-revisao-skill.md)
- [T5 — Execução no code-smells-project](task-05-projeto-1.md)
- [T6 — Execução no ecommerce-api-legacy](task-06-projeto-2.md)
- [T7 — Execução no task-manager-api](task-07-projeto-3.md)
- [T8 — Documentação e consolidação](task-08-documentacao.md)
- [T9 — Aceite final](task-09-aceite-final.md)
