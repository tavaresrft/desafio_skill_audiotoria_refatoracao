# Relatório de auditoria — <nome do projeto>

**Data:** <AAAA-MM-DD>
**Fase:** 2 — auditoria; nenhuma alteração aplicada
**Escopo examinado:** <diretórios/arquivos e limites>

## Contexto do projeto

- **Domínio:** <evidência resumida>
- **Linguagem/runtime:** <versões confirmadas ou não confirmadas e fonte>
- **Framework/dependências relevantes:** <versões e fontes>
- **Persistência/integrações:** <descrição sem segredos>
- **Comando de inicialização disponível:** <comando e fonte; dizer se não executado>
- **Arquitetura observada:** <fluxo e separação existente>
- **Inventário:** <quantidade/seleção de fontes examinadas e limitações>
- **Superfícies revisadas:** <fluxo HTTP, domínio, persistência, validação, configuração, integrações, erros, serialização, testes etc.>

## Endpoints e baseline

| Método | Caminho final | Handler/evidência | Baseline observado |
|---|---|---|---|
| <GET> | </exemplo> | `<caminho>:<linha>` | <status/campos observados ou “estático/não executado”> |

**Comandos de boot/teste identificados:** <comandos derivados e referências>.
**Limitações:** <ambiente, serviços, dados, endpoints não executados>.

## Resumo por severidade

| CRITICAL | HIGH | MEDIUM | LOW | Total |
|---:|---:|---:|---:|---:|
| <n> | <n> | <n> | <n> | <n> |

## Achados

Ordene os findings por severidade (CRITICAL, HIGH, MEDIUM, LOW); dentro de cada grupo, priorize impacto e evidência. Não complete contagem com achados duplicados ou especulativos.

### [<CRITICAL|HIGH|MEDIUM|LOW>] <título conciso — um problema>

- **Evidência:** `<caminho relativo>:<linha>` — <comportamento observável; incluir definição e uso se necessário>.
- **Condição/causa:** <o que ocorre e sob quais condições>.
- **Impacto:** <consequência concreta>.
- **Justificativa da severidade:** <relação com impacto e escala>.
- **Recomendação:** <mudança acionável; indicar eventual impacto de contrato>.
- **Confiança/limitação:** <confirmado, hipótese, versão/status não confirmados>.

<!-- Repita para cada finding independente. Não inclua valores secretos ou dados pessoais. -->

## APIs deprecated

<Nenhuma confirmada / tabela com API, pacote e versão, evidência e fonte oficial/data. Hipóteses não confirmadas devem ser identificadas como tais.>

## Escopo proposto para Fase 3

- **Correções de segurança/qualidade:** <achados e correção compatível prevista>.
- **Ajustes arquiteturais recomendados:** <achados e fronteiras necessárias; não reestruturar partes já organizadas>.
- **Contratos públicos:** <o que será preservado; incompatibilidade que exige aprovação separada>.
- **Validação planejada:** <boot, testes e lista de endpoints a exercitar, com ambiente/dados seguros>.

## Gate de confirmação

Nenhum arquivo foi alterado na Fase 1 ou 2. **Você autoriza iniciar a Fase 3 e aplicar as mudanças descritas acima?** Aguarde resposta afirmativa explícita antes de escrever qualquer arquivo.

A confirmação se limita aos achados e mudanças enumerados no escopo proposto; qualquer ampliação ou mudança incompatível de contrato requer nova decisão explícita.
