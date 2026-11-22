# T1 — Análise manual dos projetos

## Objetivo

Estabelecer uma linha de base dos problemas que a skill deve detectar e corrigir nos três projetos.

## Atividades

1. Inventariar arquivos-fonte, dependências, comandos de inicialização, rotas/endpoints e persistência de cada projeto.
2. Identificar linguagem, framework, domínio e organização arquitetural atual.
3. Revisar código em busca de problemas de arquitetura, segurança, qualidade, performance e APIs deprecated.
4. Registrar pelo menos cinco achados por projeto, com severidade, arquivo/linha, impacto e justificativa.
5. Garantir, por projeto, pelo menos um achado CRITICAL ou HIGH, dois MEDIUM e dois LOW.
6. Criar/atualizar `docs/<nome-do-projeto>/README.md` para cada alvo, registrando inventário e achados detalhados.
7. Registrar no README da raiz uma síntese da **Análise Manual** e links para os três documentos por projeto.

## Critérios de aceite

- Os três projetos foram inspecionados diretamente, sem inferir achados não confirmados no código.
- Cada projeto possui pelo menos cinco problemas classificados segundo a escala de `build.md`.
- Cada achado tem evidência rastreável (arquivo e linha ou intervalo mínimo necessário), impacto e justificativa.
- As diferenças entre o monólito Flask, o backend Express e o Flask parcialmente organizado estão descritas.
- Existe um README em `docs/` para cada projeto e o README raiz aponta para eles.

## Registro da execução

Análise estática feita diretamente nos fontes do repositório-base em
`/home/romulo/projetos/full_cycle/mba-ia-refactor-projects-skill`. Os registros
por projeto contêm stack, arquivos-fonte, dependências, inicialização,
persistência, endpoints e achados com severidade, evidência e impacto:

- [`code-smells-project`](../code-smells-project/README.md)
- [`ecommerce-api-legacy`](../ecommerce-api-legacy/README.md)
- [`task-manager-api`](../task-manager-api/README.md)

A seção **Análise Manual** do [README raiz](../../README.md) traz a síntese dos
achados. Cada projeto tem seis achados, incluindo CRITICAL/HIGH, dois MEDIUM e
dois LOW. A análise é estática; nenhum comportamento foi inferido sem evidência
no código e não foram executados testes nesta etapa.

## Checklist de conclusão

- [x] Os três projetos foram inspecionados diretamente nos fontes.
- [x] Stack, dependências, inicialização, persistência, endpoints e arquitetura foram registrados por projeto.
- [x] Cada projeto tem seis achados com severidade, evidência, impacto e justificativa.
- [x] Cada projeto atende à distribuição mínima de severidades.
- [x] Os READMEs individuais em `docs/` e a síntese no README raiz foram atualizados.
