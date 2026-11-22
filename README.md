# Refatoração arquitetural automatizada com Agent Skills

Desafio de desenvolvimento de uma skill reutilizável para analisar, auditar e refatorar APIs Flask e Express com preservação explícita de contratos.

## Análise Manual

Os fontes originais foram inspecionados no repositório-base em `/home/romulo/projetos/full_cycle/mba-ia-refactor-projects-skill`. Os relatórios manuais e evidências por arquivo/linha estão organizados por projeto:

- [code-smells-project](docs/code-smells-project/README.md): API Flask de e-commerce inicialmente monolítica.
- [ecommerce-api-legacy](docs/ecommerce-api-legacy/README.md): API Express de LMS com checkout e SQLite em memória.
- [task-manager-api](docs/task-manager-api/README.md): API Flask com separação parcial em Models, Routes, Services e Utils.

### Síntese da auditoria da skill

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---:|---:|---:|---:|---:|
| `code-smells-project` | 3 | 1 | 2 | 2 | 8 |
| `ecommerce-api-legacy` | 3 | 1 | 3 | 1 | 8 |
| `task-manager-api` | 2 | 1 | 5 | 3 | 11 |

Os detalhes, impactos, justificativas e evidências estão em [audit-project-1.md](reports/audit-project-1.md), [audit-project-2.md](reports/audit-project-2.md) e [audit-project-3.md](reports/audit-project-3.md). O projeto 3 completou as Fases 1 e 2; sua Fase 3 ainda aguarda confirmação explícita do escopo de autenticação documentado no relatório.

## Construção da Skill

A skill `refactor-arch` usa a convenção Agent Skills do Codex (`.agents/skills/refactor-arch/SKILL.md`). A cópia canônica está em `code-smells-project/.agents/skills/refactor-arch/`; as pastas completas também foram copiadas para os projetos 2 e 3 e comparadas recursivamente.

O `SKILL.md` mantém o fluxo operacional das três fases e o gate de aprovação. As referências separam heurísticas de análise, catálogo de 12 anti-patterns, template do relatório, guidelines MVC e playbook de 10 transformações antes/depois. O catálogo cobre segurança, autenticação, SQL, credenciais, responsabilidades, performance, erros, legibilidade e APIs deprecated.

A portabilidade vem de detectar stack, rotas e arquitetura pela evidência observada (manifestos, imports, composição e handlers), sem presumir nomes de arquivos, domínios ou diretórios. Flask aceita views funcionais/Blueprints e Express aceita handlers/routers; a skill preserva separações úteis e recomenda camadas apenas quando resolvem acoplamento concreto.

O fluxo exige análise estática sem escrita, relatório com evidências e severidade, revisão humana e confirmação explícita do escopo antes da Fase 3. A validação da Fase 3 cobre boot e todos os endpoints identificados, com comparação de contratos e registro do que não pôde ser executado. APIs deprecated só são relatadas após consulta às fontes oficiais para a versão permitida/instalada.

Decisões e revisão da skill estão em [T2](docs/tasks/task-02-desenho-skill-design.md) e [T4](docs/tasks/task-04-revisao-skill-review.md). A T4 reforçou a meta de cinco achados sustentáveis, a proibição de completar contagem com especulação, a autorização restrita ao escopo do relatório e a regra contra declarar “zero problemas” sem varredura documentada.

## Resultados

| Projeto | Antes | Depois / situação atual | Validação registrada |
|---|---|---|---|
| Flask e-commerce | Rotas administrativas no entrypoint; conexão SQLite global; SQL concatenado; senha em texto claro; controllers com responsabilidades misturadas. | Fábrica/composition root, configuração por ambiente, Routes, Controllers, Models/persistência, tratamento central de erros; SQL parametrizado; PBKDF2 com migração; rotas administrativas destrutivas desativadas. | Boot real; 19/19 endpoints responderam, com `410` intencional nas duas rotas administrativas. Banco temporário; hash e respostas sem senha verificados. [Log](reports/validation-project-1.md). |
| Express LMS | `AppManager` concentrava rotas/schema/checkout/relatório; segredos e cartão em log; senha com hash caseiro/default; N+1; exclusão deixava órfãos. | Rotas, controllers, serviços, repository e bootstrap separados; scrypt; transação; query agregada; exclusão consistente. Pagamento é simulado explicitamente e não declara `PAID` sem gateway real. | `npm run test:smoke` passou; `npm start` e os três endpoints foram exercitados com banco em memória. [Log](reports/validation-project-2.md). |
| Flask Task Manager | Organização parcial, mas handlers faziam ORM/regra; MD5; hash exposto; sem autorização; N+1 e seed destrutivo. | **Fase 3 pendente.** Auditoria reconheceu as camadas existentes e propôs mudanças proporcionais; nenhuma refatoração foi aplicada ainda. | Fases 1 e 2 estáticas; boot/endpoints não foram executados. Aguarda confirmação da Fase 3 em [audit-project-3.md](reports/audit-project-3.md). |

### Checklists de validação por projeto

- **Projeto 1:** Fase 1/2 concluídas; oito findings incluindo CRITICAL/HIGH; confirmação obtida; boot e 19 endpoints validados; diferenças intencionais documentadas. Registro: [T5](docs/tasks/task-05-projeto-1.md).
- **Projeto 2:** Fase 1/2 concluídas; oito findings incluindo CRITICAL/HIGH; confirmação obtida; smoke test, boot e três endpoints validados. Registro: [T6](docs/tasks/task-06-projeto-2.md).
- **Projeto 3:** Fase 1/2 concluídas; onze findings incluindo CRITICAL/HIGH; Fase 3 e validação pendentes de confirmação. Registro: [T7](docs/tasks/task-07-projeto-3.md).

As validações foram feitas em ambiente local e isolado, sem credenciais reais ou dados de cliente. No projeto 2, `npm ci` reportou 13 vulnerabilidades de dependências (2 low, 1 moderate, 8 high, 2 critical) e avisos de pacotes transitivos deprecated; não houve atualização de stack/lockfile nesta etapa. O endpoint `/api/admin/financial-report` continua sem autenticação por preservação do contrato existente e está documentado como limitação. A simulação de pagamento não é integração de gateway.

## Como Executar

### Pré-requisitos e skill

- Codex com suporte a Agent Skills e a cópia `.agents/skills/refactor-arch/` no diretório do projeto.
- Python compatível com os pins de `requirements.txt` nos projetos Flask; Node.js/npm compatíveis com `package.json`/`package-lock.json` no projeto Express.
- Abrir uma sessão Codex no diretório do projeto e solicitar: “Use a skill `refactor-arch` neste projeto”. A skill apresenta o relatório da Fase 2 e aguarda autorização antes de alterar código.

### Inicialização e validação

```bash
# code-smells-project
cd code-smells-project
pip install -r requirements.txt
APP_SECRET_KEY="<valor-aleatorio-local>" python app.py

# ecommerce-api-legacy
cd ../ecommerce-api-legacy
npm ci
npm start
npm run test:smoke

# task-manager-api (após concluir T7 e revisar o seed)
cd ../task-manager-api
pip install -r requirements.txt
python seed.py
python app.py
```

Os comandos Python usam SQLite; execute seeds somente em ambiente de desenvolvimento com banco descartável. A skill deve validar os endpoints listados no respectivo relatório e registrar status, formato/campos, limitações e evidências. Os resultados reais já executados estão nos READMEs individuais e em [validation-project-1.md](reports/validation-project-1.md) / [validation-project-2.md](reports/validation-project-2.md); o projeto 3 segue pendente de autorização/refatoração.
