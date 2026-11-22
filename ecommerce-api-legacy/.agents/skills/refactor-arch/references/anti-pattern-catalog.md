# Catálogo de anti-patterns

Use os sinais como perguntas de inspeção; um finding exige contexto, linhas e impacto concretos. Severidade indicada é padrão inicial, ajustável pela consequência real. Examine cada categoria pertinente no código efetivamente encontrado, incluindo segurança, fluxo HTTP, domínio, persistência, integração, erros, serialização e configuração. A meta do desafio é pelo menos cinco findings independentes por projeto e pelo menos um CRITICAL ou HIGH quando sustentado pela evidência. Não infle contagem: se a varredura documentada sustentar menos, explique a diferença no relatório em vez de fabricar findings.

## Segurança e integridade

### 1. Segredo hardcoded ou exposto — CRITICAL
- **Sinais:** tokens/chaves/senhas literais em código/config versionada; resposta HTTP inclui configuração sensível; logs imprimem credenciais.
- **Impacto:** acesso indevido, fraude ou comprometimento de sessão/serviço.
- **Recomendação:** remover do código e do output/log, usar configuração segura apropriada ao deploy e rotacionar segredo se houver risco de exposição. Não reproduzir o valor no relatório.

### 2. SQL/injeção ou comando arbitrário — CRITICAL
- **Sinais:** entrada HTTP interpolada/concatenada em SQL ou comando; query/admin endpoint executa texto fornecido pelo cliente; interpolação dentro de cláusulas.
- **Impacto:** leitura, alteração ou destruição de dados e possível execução não autorizada.
- **Recomendação:** parâmetros/bindings, allowlist para identificadores não parametrizáveis e remoção/proteção de execução arbitrária, preservando contrato quando seguro.

### 3. Credencial armazenada com hash inadequado — CRITICAL
- **Sinais:** senha em texto claro, MD5/SHA rápido sem KDF/salt individual, comparação determinística; logs com senha/token/cartão.
- **Impacto:** vazamento recuperável e comprometimento de contas/dados financeiros.
- **Recomendação:** mecanismo de hash de senha apropriado documentado pela stack, política de migração/rehash e exclusão de dados sensíveis dos logs. Não inventar biblioteca/versão.

### 4. Autorização ausente ou bypass — CRITICAL/HIGH
- **Sinais:** rota administrativa ou recurso de outro usuário não verifica identidade/permissão; checagem existe em middleware não montado ou usa ID controlado pelo cliente sem vínculo.
- **Impacto:** acesso ou alteração de dados fora do privilégio esperado. Classificar pelo recurso e exposição concreta.
- **Recomendação:** aplicar checagem explícita na fronteira e cobrir permitido/negado; não presumir que autenticação global esteja ativa sem rastrear composição.

### 5. Validação insuficiente na borda — MEDIUM (HIGH quando risco elevado)
- **Sinais:** valores não validados usados em persistência, pagamento, autenticação ou seleção de recurso; ausência de limites/tipos/formato; valores padrão previsíveis.
- **Impacto:** dados inconsistentes, bypass, abuso ou fluxo inválido.
- **Recomendação:** validar tipo, presença, limites e formato adequados ao contrato; preservar respostas públicas, exceto mudança incompatível explicitamente aprovada.

## Arquitetura, desempenho e manutenção

### 6. God object/handler com responsabilidades misturadas — HIGH (CRITICAL em caso extremo)
- **Sinais:** uma classe/módulo/handler registra rotas, faz SQL, valida domínio, executa integração e monta resposta; função longa com múltiplos motivos de mudança.
- **Impacto:** testes difíceis, efeito colateral cruzado e mudanças arriscadas.
- **Recomendação:** extrair fronteiras reais (handler, caso de uso/serviço, persistência) sem reestruturação em massa e sem criar abstração vazia.

### 7. Regras de domínio em rotas/controllers — HIGH
- **Sinais:** cálculos/regras repetidos em handlers; fluxo de negócio difícil de testar sem request/response; branches dominam o endpoint.
- **Impacto:** divergência de regra e acoplamento ao framework.
- **Recomendação:** mover a regra coesa para função/serviço de domínio testável e manter a rota como adaptador HTTP.

### 8. Acesso a dados e N+1 — MEDIUM
- **Sinais:** consulta dependente dentro de loop de entidades, consulta por item/usuário, carregamento integral para filtrar/agrupamento em memória.
- **Impacto:** latência, uso de memória e carga no banco crescem com volume.
- **Recomendação:** JOIN/agregação, lote/paginação ou estratégia de eager loading suportada pelo acesso atual; medir e preservar ordenação/semântica.

### 9. Tratamento de erro inconsistente ou silencioso — MEDIUM (HIGH se encobre falha crítica)
- **Sinais:** erro de callback ignorado, resposta de sucesso independente do erro persistido, `except` amplo sem registro seguro/contexto, promise rejeitada sem tratamento.
- **Impacto:** sucesso falso, estado parcial e diagnóstico difícil.
- **Recomendação:** propagar/mapear erros de forma consistente, registrar contexto não sensível e manter códigos/respostas compatíveis.

### 10. Duplicação e configuração/literais dispersos — LOW/MEDIUM
- **Sinais:** mesma validação/serialização repetida; estados/limites/configuração copiados em vários locais sem fonte única clara.
- **Impacto:** correções divergentes e manutenção frágil.
- **Recomendação:** fatorar somente duplicação real; centralizar configuração/regra quando uma fonte única reduzir inconsistência.

### 11. Mutabilidade e ruído evitáveis — LOW
- **Sinais:** `let` sem reatribuição, imports mortos, variáveis sem uso, comentários/branches obsoletos.
- **Impacto:** leitura e revisão mais difíceis.
- **Recomendação:** simplificação local e segura; não misturar grande reformatação com correções de risco.

### 12. Uso de API potencialmente deprecated — LOW/MEDIUM após confirmação
- **Sinais:** warning explícito da biblioteca, API marcada deprecated na documentação oficial da versão instalada ou regra de lint específica.
- **Impacto:** incompatibilidade futura ou perda de suporte, cujo prazo precisa de evidência.
- **Recomendação:** seguir `project-analysis.md` para confirmar status e alternativa. Sem confirmação, registrar dúvida e não classificar como deprecated.
