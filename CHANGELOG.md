# CHANGELOG

All notable changes to this project will be documented in this file.

## [v1.0.3] - 2026-11-07
### Added
- Documento de auditoria inicial da E6.3: `docs/E6_3_AUDITORIA_ARTIGO.md`, cobrindo Resumo, Abstract, Seção 1.1–1.4 e roteiro de edição para o colega.

### Fixed
- Atualização dos metadados no `docs/E6_2_ENCERRAMENTO_TECNICO.md` para refletir o pacote autenticado com SHA‑256 `F00E5DB7F445F276574CBB0185BC87BCE2D347DB078B5F74091C9060F8BE6378` e 315 entradas.

## [v1.0.2] - 2026-11-06
### Added
- Documentação de encerramento técnico `docs/E6_2_ENCERRAMENTO_TECNICO.md` (checklist final, evidências, limitações e trabalhos futuros).
- Pacote definitivo `tcc_final_product.zip`, SHA‑256 `1AA97C086412F0AFAE3352AD7C2EA738CA16EDC61E80F866E4550691C26BEE77`.

### Changed
- Reprodutibilidade em ambiente totalmente limpo registrada como **não realizada e dispensada nesta entrega** (decisão de escopo); evidências parciais já obtidas (pip install, npm ci/build, 208/208 testes, integração `/compare`).

## [v1.0.1] - 2026-11-06
### Added
- `GET /health` no frontend via `getHealth()` em `frontend/src/lib/api.ts`.
- Documentação técnica `docs/E6_1_AUDITORIA_COMPARATIVA.md` (divergências artigo × implementação, formulação E5.2, resultados consolidados).
- Documentação técnica `docs/E6_2_REVISAO_CIENTIFICA.md` (auditoria do modelo E5.2 e do AG, evidências de execução).

### Fixed
- Indicador "API online" em `frontend/src/App.tsx`: antes era texto estático; agora consulta dinamicamente `GET /api/health` e exibe "API online" ou "API offline" de forma condicional.
- README: introdução corrigida para refletir a stack real (FastAPI + React/Vite); seção do Streamlit agora rotulada como "Protótipo original em Streamlit (legado)".
- README: lista de conceitos de AG atualizada para distinguir o fitness legado (`/optimize`) e a comparação lexicográfica *feasibility-first* (`/compare`, E5.5).

### Validation
- Frontend: `npm install` / `npm ci` + `npm run build` executados com sucesso em `frontend/`; `tsc -b` e `vite build` aprovados, `dist/` gerado.
- Integração: `npm run dev` subiu em `http://localhost:5173/`, e a aba Comparação renderizou cards, convergência, histograma e tabela com dados reais do backend.

## [v1.0.0] - 2026-11-06
### Added
- Endpoint `POST /compare` (E5.5) returning `summary`, `results` (list[dict]), `histories` (list[dict]).
- Historical convergence data per seed (`histories`).
- Frontend `ComparisonPage` with cards, table, convergence chart and histogram, plus automatic state clearing on input changes.
- README updates: status Alternativa A, full contract example for `/compare`, execution instructions for backend and frontend.
- Scientific documentation (E5.4.7, E5.4.8) describing scope, mock irradiance and decision Alternativa A.
- Test suite expanded to 208 tests covering `/compare`, validation errors, retro‑compatibilidade (`/optimize`, `/baseline`).

### Fixed
- Stale results issue in `ComparisonPage` (now clears data when roof/config change and shows configuration banner).
- README outdated decision line (now correctly reflects Alternativa A).

### Deprecated
- None.

### Removed
- None.
