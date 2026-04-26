# Fontes de Dados — Licenças e Avisos

Este documento descreve, fonte por fonte, a licença declarada e as restrições legais que se aplicam aos dados acessados pelo `mcp-brasil`. **A licença MIT do código deste repositório NÃO substitui as licenças individuais de cada fonte upstream.**

> **Como ler esta tabela.** Cada fonte tem 3 dimensões avaliadas:
> - **Reuso comercial**: a licença permite uso comercial?
> - **Obras derivadas**: pode transformar/processar/redistribuir derivado?
> - **Restrições especiais**: LGPD, vedação eleitoral, restrição CNJ, etc.

> **Importante.** Em caso de dúvida ou divergência entre este documento e os termos atuais da fonte, **prevalecem os termos da fonte**. Verifique sempre o link oficial antes de uso comercial ou redistribuição em larga escala.

---

## Sumário de Risco por Categoria

| Categoria | Risco | Razão principal |
|-----------|------:|-----------------|
| Saúde (DataSUS, Imunização, ANVISA, DENASUS) | **CRÍTICO** | LGPD art. 11 §4 veda comunicação para vantagem econômica |
| Eleitoral (TSE + Meta) | **ALTO** | Lei 9.504/97; Res. TSE 23.732/2024; Meta API limitada |
| Judicial (DataJud, jurisprudência) | **ALTO** | Res. CNJ 446/2022 — chave de acesso, redistribuição vedada |
| Educação microdados (INEP) | **ALTO** | INEP removeu microdados públicos em 2022 (LGPD) |
| Segurança Pública (Atlas Violência, FBSP) | **ALTO** | Licença restritiva — sem uso comercial, sem derivadas |
| Transparência Federal (CGU/Transparência) | Baixo | Open data; uso comercial permitido com atribuição |
| Geografia/Estatística (IBGE) | Baixo | Open data com atribuição |
| Economia (BACEN, IPEA) | Baixo | Open data; algumas séries com atribuição |
| Legislativo (Câmara, Senado) | Baixo | Open data; atribuição |
| Compras Públicas (PNCP) | Baixo | Lei 14.133/21 — publicidade obrigatória |
| Mercado financeiro (B3 via brapi) | Médio | brapi.dev é terceiro; TOS próprio |
| Aviação ao vivo (OpenSky) | Médio | OpenSky Network — TOS não-comercial em parte |

---

## 1. Saúde — RISCO CRÍTICO

### 1.1. `imunizacao` — SI-PNI / vacinação

- **Origem**: Sistema de Informação do Programa Nacional de Imunizações (Ministério da Saúde)
- **Licença declarada**: Creative Commons **Atribuição-SemDerivações 3.0** (CC BY-ND 3.0) via OpenDataSUS
- **Reuso comercial**: permitido com atribuição
- **Obras derivadas**: **PROIBIDAS** pela CC BY-ND
- **Risco LGPD**: Art. 11 (dados sensíveis) e §4 (vedação de comunicação para vantagem econômica)

**Disclaimer obrigatório:**
> Dados de imunização são **dados pessoais sensíveis** sob LGPD art. 5, II. Mesmo agregados, podem permitir re-identificação por município + data + faixa etária. **VEDADO uso comercial envolvendo identificação de indivíduos** (LGPD art. 11 §4). Atribuição: Ministério da Saúde / SI-PNI / OpenDataSUS.

### 1.2. `saude` — CNES/DataSUS

- **Origem**: Cadastro Nacional de Estabelecimentos de Saúde
- **Licença**: dados públicos por força da LAI (Lei 12.527/11)
- **Risco**: nomes, CRM e local de profissionais expõem dado pessoal — LGPD art. 7

**Disclaimer obrigatório:**
> Profissionais de saúde têm proteção de privacidade (Lei 12.842/13, resoluções CFM). **VEDADO uso para localização, contato direto não solicitado, ou marketing.** Dados de leitos podem agregar PII; tratar como dado sensível.

### 1.3. `opendatasus` — datasets DataSUS via CKAN

- **Origem**: opendatasus.saude.gov.br
- **Licença**: **CC BY-ND 3.0** (Atribuição-SemDerivações)
- **Conflito potencial**: o servidor mcp-brasil **transforma** payloads JSON, formata, agrega — pode caracterizar "obra derivada" vedada pela ND.

**Mitigação:** disponibilizar dados em estado mais próximo possível do bruto; documentar transformações como "apresentação técnica", não derivação editorial.

### 1.4. `anvisa` — bulário, medicamentos, preços CMED

- **Origem**: ANVISA
- **Licença**: dados públicos por LAI; alguns datasets em CKAN (open license)
- **Atribuição**: ANVISA, com link para registro original

### 1.5. `denasus` — auditorias do SUS

- **Origem**: Departamento Nacional de Auditoria do SUS
- **Licença**: dados públicos LAI
- **Risco**: dados de auditoria podem incluir nomes de gestores, prestadores; tratar com cuidado

### 1.6. `bps` — Banco de Preços em Saúde

- **Origem**: Ministério da Saúde
- **Licença**: open data CGU
- **Atribuição**: BPS / Ministério da Saúde

### 1.7. `farmacia_popular` e `rename`

- **Origem**: Ministério da Saúde — programa Farmácia Popular e RENAME
- **Licença**: open data CGU; atribuição
- **Disclaimer**: dados de farmácias credenciadas não devem ser usados para marketing direto

---

## 2. Eleitoral — RISCO ALTO

### 2.1. `tse` (REST) e datasets locais TSE — `tse_candidatos`, `tse_bens`, `tse_votacao`, `tse_redes_sociais`, `tse_fefc`

- **Origem**: Tribunal Superior Eleitoral — Portal de Dados Abertos (dadosabertos.tse.jus.br)
- **Licença**: dados abertos com atribuição
- **Restrição especial — Resolução TSE 23.732/2024**: tratamento de dados sensíveis em propaganda eleitoral exige consentimento explícito
- **Restrição especial — Lei 9.504/97**: regras de propaganda eleitoral aplicam-se a 3 meses antes / 30 dias depois do pleito

**Disclaimer obrigatório:**
> Dados eleitorais. **VEDADO** uso para: (a) propaganda eleitoral irregular (Lei 9.504/97), (b) abuso de poder econômico em campanha, (c) tratamento de dados sensíveis (cor/raça, religião, opinião política dos candidatos) sem base legal. Patrimônio declarado de candidatos é público mas seu cruzamento com outros dados pode caracterizar tratamento de dado pessoal sob LGPD. Atribuição: Tribunal Superior Eleitoral.

### 2.2. `anuncios_eleitorais` — Meta Ad Library

- **Origem**: Meta Platforms (Facebook/Instagram) — `https://www.facebook.com/ads/library/api/`
- **Licença**: **NÃO é dado público brasileiro**. Sujeito aos Termos de Uso da Meta Ad Library API.
- **Limitação 2026**: a API tem restringido acesso a anúncios fora da União Europeia. Anúncios eleitorais brasileiros podem **não estar mais disponíveis** via API pública.

**Disclaimer obrigatório:**
> Esta tool consulta API DE TERCEIRO (Meta Platforms, Inc.). Você é o operador perante a Meta — leia e cumpra os [Termos da Meta Ad Library API](https://www.facebook.com/ads/library/api/). Em 2026, a cobertura para anúncios brasileiros pode estar reduzida. **VEDADA** redistribuição que viole o TOS da Meta.

---

## 3. Judicial — RISCO ALTO

### 3.1. `datajud` — DataJud/CNJ

- **Origem**: Conselho Nacional de Justiça
- **Licença**: API autenticada — Resolução CNJ 331/2020 e 446/2022
- **Acesso**: chave de API gerada pelo Departamento de Pesquisas Judiciárias do CNJ
- **Restrição**: **VEDADA redistribuição em larga escala**, mineração extensiva ou criação de bases derivadas comerciais sem termo específico assinado com o CNJ

**Disclaimer obrigatório:**
> Dados judiciais via DataJud têm acesso regulamentado pelo CNJ (Res. 331/2020, 446/2022). Você precisa de **chave de API própria**. Nomes de partes, CPF, e detalhes de processos sensíveis (Vara da Família, Infância, Penal de menor potencial) **devem ser tratados como dados pessoais sob LGPD**. Vedada redistribuição em massa. Atribuição: Conselho Nacional de Justiça.

### 3.2. `jurisprudencia` — STF, STJ, TST

- **Origem**: portais oficiais de busca (web)
- **Licença**: acórdãos publicados são informação pública (LAI); marca dos tribunais permanece com eles
- **Risco**: scraping pode violar TOS dos portais; rate limiting próprio

---

## 4. Educação — RISCO ALTO

### 4.1. `inep` (REST) e datasets `inep_enem`, `inep_censo_escolar`

- **Origem**: Instituto Nacional de Estudos e Pesquisas Educacionais Anísio Teixeira
- **Histórico crítico**: em 2022, INEP **REMOVEU os microdados de ENEM e Censo Escolar do acesso público** por exigência da LGPD. Acesso passou a ser via SEDAP (Serviço de Acesso a Dados Protegidos), com cadastro e termo de compromisso.
- **Implicação**: datasets `inep_enem` e `inep_censo_escolar` deste projeto podem estar utilizando snapshots PRÉ-2022 (dados retirados de circulação) ou versões reformatadas (anonimizadas).

**Ação recomendada AO TITULAR DO PROJETO:**
1. Verificar a origem (URL, snapshot date) dos arquivos baixados pelos datasets `inep_enem` e `inep_censo_escolar`
2. Se forem versões pré-2022 não anonimizadas, **REMOVER do projeto** e substituir por acesso via SEDAP
3. Se forem versões oficiais pós-LGPD, manter atribuição clara

**Disclaimer obrigatório (até verificação):**
> ⚠️ Verificação de conformidade pendente. INEP removeu microdados públicos em 2022 por LGPD. **NÃO usar dados deste módulo até confirmar origem.** Pesquisas formais devem usar SEDAP/INEP.

### 4.2. `fnde` — repasses, merenda, PNATE

- **Origem**: Fundo Nacional de Desenvolvimento da Educação
- **Licença**: open data CGU; atribuição

---

## 5. Segurança Pública — RISCO ALTO

### 5.1. `atlas_violencia` — Atlas da Violência (IPEA + FBSP)

- **Origem**: Instituto de Pesquisa Econômica Aplicada + Fórum Brasileiro de Segurança Pública
- **Licença**: **PROIBIDO uso comercial e obras derivadas**. Reprodução permitida apenas para uso educacional/informativo, com atribuição.

**Conflito direto com licença MIT do código.**

**Ação recomendada AO TITULAR DO PROJETO:**
- Avaliar **remoção** desta feature, OU
- Restringir programaticamente: tool retorna apenas links para o Atlas oficial, não os dados em si, OR
- Buscar autorização escrita de IPEA + FBSP

**Disclaimer obrigatório (enquanto presente):**
> Atlas da Violência é obra protegida do IPEA e Fórum Brasileiro de Segurança Pública. **VEDADO uso comercial e criação de obras derivadas.** Reprodução apenas para fins educativos/informativos com atribuição completa: "Atlas da Violência [ano] — IPEA / Fórum Brasileiro de Segurança Pública".

### 5.2. `forum_seguranca` — Anuário FBSP

- **Origem**: Fórum Brasileiro de Segurança Pública (entidade privada)
- **Licença**: similar ao Atlas — restritiva. Verificar termos por publicação.
- **Risco igual ao 5.1**

### 5.3. `sinesp` — SINESP/MJSP

- **Origem**: Ministério da Justiça e Segurança Pública
- **Licença**: open data CGU
- **Risco LGPD**: dados do sistema penitenciário (INFOPEN) tocam em dados sensíveis sobre pessoas privadas de liberdade

### 5.4. `isp_rj` (dataset) — Instituto de Segurança Pública RJ

- **Origem**: Governo do Estado do Rio de Janeiro
- **Licença**: open data; atribuição
- **Risco**: estatísticas por CISP podem ser usadas para narrativas estigmatizantes; manter contexto

### 5.5. `mj` — MJSP CKAN (PROCONs, INFOPEN, armas, sistema prisional)

- **Origem**: Ministério da Justiça e Segurança Pública
- **Licença**: open data CGU
- **Risco**: dados de armas registradas podem incluir CPF do titular — tratamento sob LGPD

---

## 6. Transparência Federal — Baixo Risco

### 6.1. `transparencia` — Portal da Transparência (CGU)

- **Origem**: Controladoria-Geral da União
- **Licença**: dados abertos; reuso comercial **permitido** com atribuição
- **Atribuição**: "Portal da Transparência do Governo Federal — CGU"

**Disclaimer obrigatório:**
> Servidores públicos têm proteção de privacidade ampliada — CPF é mascarado pela origem. **NÃO desmascare CPF se obtido por outras fontes.** Salários e cargos são públicos por força da LAI; uso para perseguição/assédio é vedado por essa lei e pelo Marco Civil.

### 6.2. `tcu` — Tribunal de Contas da União

- **Origem**: TCU
- **Licença**: dados públicos LAI; atribuição

### 6.3. `tce_*` (12 features estaduais)

- **Origem**: Tribunais de Contas Estaduais
- **Licença**: variável por estado; predominantemente open data
- **Atribuição**: especificar TCE de origem por consulta

### 6.4. `siconfi` — Tesouro Nacional

- **Origem**: Secretaria do Tesouro Nacional
- **Licença**: open data; atribuição

### 6.5. `transferegov` — emendas parlamentares PIX

- **Origem**: Plataforma TransfereGov
- **Licença**: open data; atribuição

### 6.6. `spu_geo`, `spu_imoveis`, `spu_siapa` — Secretaria do Patrimônio da União

- **Origem**: SPU
- **Licença**: open data; atribuição

---

## 7. Economia e Finanças — Baixo Risco

### 7.1. `bacen`, `bcb_olinda` — Banco Central

- **Origem**: BCB
- **Licença**: dados abertos via Portal de Dados Abertos do BCB; atribuição

### 7.2. `ipeadata` — IPEA

- **Origem**: Instituto de Pesquisa Econômica Aplicada
- **Licença**: open data; atribuição
- **Atenção**: NÃO confundir com Atlas da Violência (mesmo IPEA, licença diferente)

### 7.3. `bndes` — BNDES

- **Origem**: Banco Nacional de Desenvolvimento
- **Licença**: open data; atribuição

### 7.4. `cvm_fundos` (dataset)

- **Origem**: Comissão de Valores Mobiliários
- **Licença**: dados públicos por LC 6.385/76; atribuição

### 7.5. `b3` (via brapi.dev)

- **Origem**: brapi.dev (terceiro privado, não é a B3 oficial)
- **Licença**: TOS próprio do brapi.dev (cadastro, rate limit)
- **Risco**: terceiro pode mudar TOS, encerrar serviço, ou ter problemas com a B3

**Disclaimer obrigatório:**
> Cotações via brapi.dev — **terceiro privado**, NÃO é fonte oficial da B3. Para uso profissional/regulatório, consulte a B3 diretamente.

### 7.6. `anp_precos` (dataset)

- **Origem**: Agência Nacional do Petróleo
- **Licença**: open data; atribuição

---

## 8. Geografia, Estatística — Baixo Risco

### 8.1. `ibge` — Instituto Brasileiro de Geografia e Estatística

- **Origem**: IBGE
- **Licença**: dados abertos com atribuição; uso comercial permitido em quase todos os datasets
- **Atenção**: alguns dados (como mapas do Atlas) têm proteção autoral específica

---

## 9. Legislativo — Baixo Risco

### 9.1. `camara`, `senado`, `governadores`

- **Origem**: Câmara dos Deputados, Senado Federal
- **Licença**: dados abertos; atribuição
- **Documentação**: dadosabertos.camara.leg.br, legis.senado.leg.br

---

## 10. Meio Ambiente — Baixo Risco

### 10.1. `inpe` — INPE (queimadas, desmatamento)

- **Origem**: Instituto Nacional de Pesquisas Espaciais
- **Licença**: dados abertos; atribuição

### 10.2. `ana` — Agência Nacional de Águas

- **Origem**: ANA
- **Licença**: open data; atribuição

### 10.3. `ibama` — IBAMA (CKAN)

- **Origem**: Instituto Brasileiro do Meio Ambiente
- **Licença**: open data; atribuição

---

## 11. Energia, Infraestrutura, Aviação — Risco Variável

### 11.1. `aneel`, `antt`

- **Origem**: agências reguladoras (CKAN)
- **Licença**: open data; atribuição

### 11.2. `anac_*` (datasets) — ANAC RAB, voos, tarifas, pontualidade

- **Origem**: Agência Nacional de Aviação Civil
- **Licença**: open data; atribuição

### 11.3. `opensky` — OpenSky Network

- **Origem**: OpenSky Network (consórcio europeu sem fins lucrativos)
- **Licença**: **NÃO é dado oficial brasileiro**. TOS próprio do OpenSky.
- **Restrição**: uso não-comercial em parte do dataset; verificar TOS atual

**Disclaimer obrigatório:**
> OpenSky Network é fonte de TERCEIRO. Uso sujeito aos termos do OpenSky. Para vigilância de aeronaves brasileiras com finalidade regulatória, consulte ANAC/DECEA.

---

## 12. Compras Públicas — Baixo Risco

### 12.1. `compras` — PNCP + ComprasNet/SIASG

- **Origem**: Portal Nacional de Contratações Públicas + Ministério da Gestão
- **Licença**: publicidade obrigatória sob Lei 14.133/2021
- **Risco**: CNPJ de fornecedores é dado público; CPF de pessoas físicas exige cuidado

---

## 13. Diários Oficiais — Baixo Risco

### 13.1. `diario_oficial` — Querido Diário + DOU

- **Origem**: Open Knowledge Brasil (Querido Diário) + Imprensa Nacional (DOU)
- **Licença**: **CC BY 4.0** (Querido Diário); LAI para DOU
- **Atribuição**: "Querido Diário — Open Knowledge Brasil" e/ou "Imprensa Nacional"

---

## 14. Utilidades — Baixo Risco

### 14.1. `brasilapi`

- **Origem**: BrasilAPI (projeto comunitário, brasilapi.com.br)
- **Licença**: MIT
- **Atribuição**: BrasilAPI

### 14.2. `dados_gov_br` — catálogo dados.gov.br

- **Origem**: dados.gov.br (CGU)
- **Licença**: open data; atribuição

### 14.3. `tabua_mares`, `noticias`

- **Origem**: Marinha (Tábua de Marés); RSS de Câmara, Senado, Agência Brasil, BCB
- **Licença**: open data / fair use de RSS
- **Risco**: RSS aggregation deve manter atribuição e link para fonte original

---

## 15. Agentes — `redator`

- **Origem**: feature interna de mcp-brasil
- **Licença**: MIT (parte do código deste repositório)
- **Risco**: agente que GERA conteúdo (não apenas consulta) ativa toda a discussão de responsabilidade por IA generativa — ver ACCEPTABLE_USE.md

---

## Cláusula geral de atribuição

Sempre que possível, retorne ao usuário final junto à resposta:

```
Fonte: <NOME DA FONTE OFICIAL>
URL: <link para o registro original>
Acessado em: <timestamp ISO 8601>
Licença da fonte: <CC BY 4.0 / open data / etc.>
```

Isso satisfaz o requisito de atribuição da maioria das licenças open data brasileiras e da CC BY-ND 3.0.

---

## Atualização e revisão

Este documento foi escrito em **2026-04-26** com base nos termos vigentes das fontes naquela data. Licenças e termos de uso de APIs governamentais brasileiras podem mudar sem aviso prévio. **Recomenda-se revisão semestral** desta tabela.

Reportes de inconsistência: abrir issue no repositório com o label `legal:sources`.
