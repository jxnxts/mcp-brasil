MA# TECH_DEBT.md — Interactive TODO for Technical Debt

> Track bugs, incompatibilities, mocks, and incomplete implementations.
> Update this file whenever you find something that needs attention later.

## Legend

- `[ ]` — Open (needs work)
- `[~]` — In progress
- `[x]` — Resolved

---

## Bootstrap Phase

- [x] **mount() API mismatch** — `feature.py` used `mount("/path", server)` instead of FastMCP v3's `mount(server, namespace=name)`. Fixed.
- [x] **list_tools() accessed private API** — `_tool_manager._tools` is private FastMCP internals. Removed method to avoid mypy strict failures.
- [ ] **_shared/http_client.py not implemented** — ADR-001 mentions shared HTTP client with retry + backoff + rate-limit. Needed before first feature (IBGE).
- [ ] **_shared/cache.py not implemented** — LRU cache with TTL mentioned in ADR-001. Planned for Semana 2.
- [ ] **_shared/formatting.py not implemented** — LLM response formatting utilities. Create when first feature needs it.
- [ ] **settings.py not implemented** — Global config (env vars, defaults) mentioned in ADR-001 structure.

## Known Limitations

- [ ] **No CONTRIBUTING.md** — Mentioned in roadmap Semana 0 but not yet created.
- [ ] **No GitHub Actions CI** — `ruff → mypy → pytest` pipeline not configured yet.
- [ ] **pyproject.toml uses optional-dependencies instead of dependency-groups** — `uv sync --group dev` fails, must use `uv sync --extra dev`.

---

*Last updated: 2026-03-22*
