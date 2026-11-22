# T4 — Revisão de cobertura e portabilidade da skill

## Objetivo

Revisar a skill antes de aplicá-la aos projetos, reduzindo lacunas de detecção e risco de mudanças incompatíveis.

## Atividades

1. Conferir cada requisito de `build.md` contra o `SKILL.md` e as referências.
2. Verificar se os sinais de detecção são observáveis e se orientam o agente a confirmar evidências no código.
3. Revisar instruções para evitar atribuir severidade sem justificativa, declarar “zero problemas” sem varredura ou alegar validação não executada.
4. Confirmar que a fase de auditoria produz relatório antes de solicitar confirmação e que o aceite cobre exatamente o escopo proposto.
5. Verificar consistência das cópias nos três projetos.

## Critérios de aceite

- Todos os requisitos mínimos do catálogo, playbook, template e gates estão mapeados.
- A skill funciona por descoberta do contexto, sem pressupor stack, domínio ou estrutura fixa.
- Nenhuma instrução permite iniciar a Fase 3 sem confirmação explícita.
- Lacunas encontradas foram corrigidas antes das execuções.

## Checklist de conclusão

- [x] Requisitos de `build.md` foram mapeados para skill e referências.
- [x] Sinais e evidências de detecção foram revisados.
- [x] Severidades e alegações de validação têm critérios explícitos.
- [x] A confirmação explícita bloqueia a Fase 3.
- [x] Portabilidade para as três stacks/estruturas foi revisada.
- [x] Lacunas encontradas foram corrigidas e as cópias comparadas.

Registro da revisão: [task-04-revisao-skill-review.md](task-04-revisao-skill-review.md).
