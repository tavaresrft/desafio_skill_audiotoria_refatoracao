# T3 — Implementação da skill e arquivos de referência

## Objetivo

Construir a skill completa, mantendo instruções operacionais concisas e conhecimento detalhado nos arquivos Markdown de referência.

## Atividades

1. Criar `.claude/skills/refactor-arch/SKILL.md` (ou localização equivalente da ferramenta escolhida), com as três fases, gates e regras de segurança operacional.
2. Criar referência de análise de projeto: heurísticas para linguagem, framework, banco, domínio, inventário e arquitetura.
3. Criar catálogo com pelo menos oito anti-patterns, sinais específicos de detecção, severidade, impacto e recomendação; distribuir achados entre CRITICAL, HIGH, MEDIUM e LOW.
4. Incluir detecção de APIs deprecated, como confirmar obsolescência na stack encontrada e recomendar substituto atual sem inventar versões.
5. Criar template padronizado do relatório da Fase 2, com resumo por severidade, contexto, achados e evidências de arquivo/linha.
6. Criar guidelines MVC e playbook com pelo menos oito transformações concretas, cada uma com exemplo antes/depois aplicável às stacks cobertas.
7. Incluir validação pós-refatoração: boot, teste dos endpoints originais e comparação de contratos/respostas quando possível.
8. Copiar a pasta completa da skill para os projetos 2 e 3, preservando igualdade dos arquivos de referência.

## Critérios de aceite

- O nome `refactor-arch` e `SKILL.md` são mantidos.
- As cinco áreas obrigatórias estão cobertas em Markdown.
- Existem no mínimo oito anti-patterns e oito transformações antes/depois.
- A confirmação humana é um bloqueio explícito entre auditoria e qualquer escrita/refatoração.
- As instruções distinguem recomendações de arquitetura de correções de segurança/qualidade e se adaptam à estrutura observada.
- As três cópias da skill são idênticas, salvo necessidade documentada da ferramenta.

## Checklist de conclusão

- [x] `SKILL.md` implementa as três fases e os gates de segurança.
- [x] As referências cobrem análise de projeto, catálogo, template, MVC e playbook.
- [x] O catálogo contém ao menos oito anti-patterns e inclui APIs deprecated.
- [x] O playbook contém ao menos oito transformações com exemplos antes/depois.
- [x] A confirmação humana bloqueia qualquer escrita da Fase 3.
- [x] A validação pós-refatoração cobre boot e endpoints originais.
- [x] As cópias da skill foram verificadas nos três projetos.

Implementação canônica: `code-smells-project/.agents/skills/refactor-arch/`. Cópias integrais: `ecommerce-api-legacy/.agents/skills/refactor-arch/` e `task-manager-api/.agents/skills/refactor-arch/`.
