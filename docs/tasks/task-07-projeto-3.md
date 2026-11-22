# T7 — Executar e refatorar `task-manager-api`

## Objetivo

Validar que a skill reconhece problemas em uma API Flask que já possui organização parcial em camadas.

## Atividades

1. Copiar/conferir a skill no projeto 3 e executar a Fase 1.
2. Validar identificação de Python/Flask, domínio Task Manager, arquivos e camadas existentes.
3. Executar a Fase 2 e conferir achados de arquitetura, segurança, performance e qualidade; salvar `reports/audit-project-3.md` na raiz.
4. Confirmar pelo menos cinco findings, incluindo um CRITICAL ou HIGH, sem tratar a mera existência de pastas como prova de arquitetura adequada.
5. Revisar e confirmar explicitamente a Fase 3.
6. Aplicar somente mudanças justificadas, preservando estrutura útil e todos os endpoints existentes.
7. Validar boot e endpoints; registrar comandos, resultados e eventuais limitações.
8. Atualizar `docs/task-manager-api/README.md` com o relatório, resumo antes/depois, mudanças realizadas, comandos e evidências reais de validação, além de limitações conhecidas.
9. Preparar e registrar o commit do código refatorado do projeto 3 no fork.

## Critérios de aceite

- Stack e domínio detectados corretamente, com reconhecimento da organização parcial.
- Auditoria identifica problemas concretos mesmo com Models/Routes/Services/Utils existentes.
- Relatório existe no caminho exigido e satisfaz o mínimo de achados.
- API inicia sem erros e todos os endpoints originais respondem após as mudanças.
- O README do projeto em `docs/` registra os resultados sem declarar validações não executadas.
- Melhorias arquiteturais são proporcionais e não implicam reorganização cosmética sem benefício.
- O código refatorado está commitado no repositório de entrega.

## Checklist de conclusão

- [x] Skill foi copiada/conferida e Fase 1 identificou Flask, domínio e camadas existentes.
- [x] Relatório da Fase 2 foi salvo em `reports/audit-project-3.md` e comparado à análise manual.
- [x] Auditoria identificou achados concretos além da existência de camadas.
- [ ] Confirmação explícita foi obtida antes de iniciar a Fase 3.
- [ ] Refatoração preservou as partes úteis e os contratos públicos.
- [ ] Boot e todos os endpoints originais foram validados com evidência registrada.
- [ ] `docs/task-manager-api/README.md` foi atualizado com resultados e limitações.
- [ ] Código refatorado foi commitado no repositório de entrega.

Relatório atual: [`reports/audit-project-3.md`](../../reports/audit-project-3.md). Nenhum arquivo da aplicação foi alterado; aguarda-se a confirmação do gate da Fase 2.
