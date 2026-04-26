# Política de Uso Aceitável (Acceptable Use Policy)

**Versão:** 1.0 — 2026-04-26
**Aplicabilidade:** este documento é parte integrante do licenciamento do `mcp-brasil`. Ao instalar, executar, integrar ou redistribuir este software, você concorda com esta Política em conjunto com a [licença MIT](LICENSE), o [NOTICE](NOTICE) e o [SOURCES.md](SOURCES.md).

---

## 1. Princípios

O `mcp-brasil` existe para tornar dados públicos brasileiros acessíveis a agentes de IA, em benefício de jornalismo, pesquisa, educação e engajamento cívico. Esta Política assegura que o uso do software permaneça alinhado a esse propósito e à legislação brasileira.

---

## 2. Vedações Específicas

### 2.1. Saúde — LGPD art. 11 §4

É **VEDADO** usar este software para:

- Acessar dados de imunização (`imunizacao`), saúde pública (`saude`, `opendatasus`, `denasus`, `bps`), Farmácia Popular (`farmacia_popular`) ou medicamentos prescritos (`rename`) com **objetivo de obter vantagem econômica** envolvendo identificação de indivíduos.
- Cruzar dados de vacinação ou estabelecimentos de saúde com dados pessoais de outras fontes para fins de marketing, scoring, seguro, plano de saúde ou recrutamento.
- Re-identificar pessoas a partir de dados agregados.

**Base legal:** LGPD (Lei 13.709/2018) art. 11 §4 — *"É vedada a comunicação ou o uso compartilhado entre controladores de dados pessoais sensíveis referentes à saúde com objetivo de obter vantagem econômica..."*.

### 2.2. Eleitoral — Lei 9.504/97 e Resoluções TSE

É **VEDADO** usar este software para:

- Propaganda eleitoral irregular ou abuso de poder econômico em campanha (Lei 9.504/97).
- Mineração de redes sociais de candidatos (`tse_redes_sociais`) ou anúncios pagos (`anuncios_eleitorais`) com fim de prejuízo a candidatura adversária.
- Tratamento de dados sensíveis de candidatos (cor/raça, opinião política implícita, religião) sem consentimento ou base legal específica (LGPD art. 11; Res. TSE 23.732/2024).
- Construção de "listas negras" eleitorais ou perfilamento de eleitores.

Em **período eleitoral** (3 meses antes / 30 dias depois do pleito), recomenda-se cautela adicional e consulta a advogado eleitoral.

### 2.3. Judicial — Resolução CNJ 446/2022 e LGPD

É **VEDADO**:

- Redistribuir em larga escala (bulk download, mirror, dataset público) os dados obtidos via DataJud.
- Construir base derivada comercial (ex.: sistema de "consulta de antecedentes") sem termo específico assinado com o CNJ.
- Identificar, expor ou perseguir pessoas a partir de partes de processos.
- Acessar processos sob segredo de justiça através de proxies ou contornos do mascaramento padrão.

### 2.4. PII (Dados Pessoais Identificáveis)

É **VEDADO** desabilitar o mascaramento padrão de PII (CPF, CNPJ pessoal, e-mail, telefone, nomes em processos) sem **base legal documentada** sob LGPD art. 7 ou art. 11. A variável de ambiente `MCP_BRASIL_LGPD_ALLOW_PII` existe para casos legítimos (jornalismo investigativo, pesquisa acadêmica, autoridade pública) e ativá-la **transfere a você** a responsabilidade de controlador sob LGPD.

### 2.5. Conteúdo gerado por IA

Este servidor é uma camada de acesso a dados. Modelos de IA que o consomem podem **alucinar**, distorcer, ou interpretar mal as respostas. É **VEDADO**:

- Apresentar saídas de IA como "dado oficial" sem verificação na fonte.
- Usar este software para gerar conteúdo jornalístico, jurídico, médico ou financeiro definitivo sem revisão humana qualificada.
- Construir produto que omita ao usuário final a natureza não-determinística dos modelos de IA intermediários.

A jurisprudência brasileira (ex.: TJ-PR 2025) já reconhece **responsabilidade objetiva** por danos causados por sistemas de IA com falha de design.

### 2.6. Símbolos e marcas oficiais

É **VEDADO** usar este software como base para:

- Apresentar-se como serviço, parceiro ou afiliado de IBGE, BACEN, TSE, CNJ, CGU, ANVISA, INPE, IPEA, ANA ou qualquer outra instituição cujos dados são acessados.
- Reproduzir logos, brasão ou armas oficiais (Lei 5.700/71) em produtos derivados sem autorização das instituições.
- Construir copy ou interface que sugira oficialidade (cores nacionais como elemento dominante, denominação confundível com órgão público, etc.).

### 2.7. Categorias de uso vedadas em qualquer hipótese

- **Perseguição** (assédio, stalking, doxing) de pessoas físicas
- **Discriminação** ou estigmatização de comunidades, grupos étnicos, regiões
- **Fake news** apresentadas como dado oficial
- **Vigilância** de cidadãos sem amparo legal
- **Concorrência desleal** (uso para construir produto que se faça passar por oficial, art. 195 LPI)

---

## 3. Obrigações Positivas do Operador

Quem opera este servidor para uso de terceiros (SaaS, integração interna, agente público) **DEVE**:

1. **Atribuir corretamente** cada fonte de dado conforme [SOURCES.md](SOURCES.md), seja na resposta ao usuário, seja em nota de rodapé do produto.
2. **Manter mascaramento de PII** ativo por padrão; só desativar com base legal documentada.
3. **Avisar usuários finais** sobre a natureza dos dados (público mas não anônimo, possibilidade de erro, IA pode alucinar).
4. **Respeitar rate limits** das APIs upstream — não distribuir o ônus de scraping coletivo.
5. **Cooperar com solicitações de remoção** de titulares de dados (LGPD art. 18) repassadas por usuários finais.
6. **Reportar incidentes** envolvendo dados pessoais via canal `incidents@<seu-domínio>` (ou crie um) e à ANPD se aplicável (art. 48 LGPD).

---

## 4. Não-Oficialidade

`mcp-brasil` é **projeto independente da comunidade open source**, mantido por contribuidores voluntários. **NÃO** é serviço, programa, parceria ou iniciativa de:

- Governo Federal do Brasil
- Qualquer Ministério, Agência Reguladora, Autarquia ou Tribunal cujos dados sejam acessados
- Anthropic (criadora do protocolo MCP)
- Qualquer modelo de IA cliente (Claude, GPT, Copilot, etc.)

A referência a "Brasil" no nome do projeto descreve seu objeto (dados públicos brasileiros) e não vinculação institucional.

---

## 5. Consequências de Descumprimento

Os mantenedores do `mcp-brasil` reservam-se o direito de:

- Encerrar suporte, responder issues, ou aceitar contribuições de operadores em violação reiterada desta Política
- Cooperar com autoridades (ANPD, MP, TSE, CNJ) em investigações sobre uso indevido
- Tornar pública (via README, CHANGELOG ou avisos no PyPI) a identificação de operadores que façam uso massivo do software para fins vedados, quando legalmente possível

---

## 6. Reporte de Abuso

Suspeita de uso em violação desta Política:

- Issues do GitHub: https://github.com/Mcp-Brasil/mcp-brasil/issues — label `acceptable-use`
- E-mail: a definir pelo titular (sugestão: `abuse@<dominio>`)

Os mantenedores avaliarão de boa-fé e tomarão as medidas cabíveis.

---

## 7. Limitação Adicional de Responsabilidade

Em complemento à cláusula de "AS IS" da licença MIT:

- Os mantenedores **não assumem responsabilidade** por consequências decorrentes do descumprimento desta Política por operadores terceiros.
- A responsabilidade pelo cumprimento da LGPD, Lei Eleitoral, Lei de Acesso à Informação, regulamentação setorial (CNJ, ANS, etc.) e dos termos das APIs upstream é **integralmente do operador**.
- Em caso de demanda judicial movida contra o operador por uso deste software, o operador concorda em **não chamar os mantenedores** ao processo, salvo nas hipóteses legalmente inafastáveis.

---

## 8. Atualização desta Política

Esta Política pode ser atualizada conforme:

- Mudanças na legislação brasileira (LGPD, Marco Civil, PL 2338/2023 quando aprovado)
- Novas resoluções de ANPD, TSE, CNJ, INPI
- Novas fontes de dados adicionadas ou removidas

Versões anteriores serão mantidas no histórico do Git. Operadores que mantenham instalações de longo prazo devem **revisar esta política a cada release minor** do `mcp-brasil`.
