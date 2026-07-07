# AGENTS.md — Edurata Functions

Notes for AI agents editing functions in this repository. Each published function is deployed as an **isolated** Lambda (or container): only files matched by `.edufc.yml` `include` and dependencies from **`package.json`** (Node) or **`requirements.txt`** (Python) are present at runtime.

**Canonical schema:** `../edurata-yaml/schema.json`  
**Workflow usage:** `../edurata-workflows/AGENTS.md`

---

## Function layout

Each function lives in its own directory with a `.edufc.yml` (or `.edufc.yaml`) beside the entrypoint:

```
general/axios/
  .edufc.yaml
  package.json          # Node — piped through npm install at deploy
  src/index.ts
  dist/tsc/index.js     # built artifact; include dist/tsc/**

etl/extract/extract-text-from-webpage/
  .edufc.yml
  requirements.txt      # Python — pip install -r requirements.txt -t . at deploy
  index.py
```

| Runtime | Dependency file | Handler |
| --- | --- | --- |
| `nodejs20` | `package.json` in the **function directory** | `exports.handler` in `entrypoint` (default `index.js`) |
| `python3_10` | `requirements.txt` in the **function directory** | `def handler(inputs)` in `entrypoint` (default `index.py`) |
| `docker` | Image / Dockerfile | Platform-defined |

Optional `.edufc.yml` fields: `entrypoint`, `include`, `exclude`, `packages` (inline-only deps).

---

## `include` and the deployment zip

On git deploy, the platform:

1. Clones the repo subpath from `source.path` (that directory is the build **cwd**).
2. Installs deps from `package.json` or `requirements.txt` in that directory.
3. Zips only paths returned by `include` globs (plus `entrypoint` and installed deps).

Zip entry names are the **glob path as matched from cwd** (e.g. `index.py`, `dist/tsc/index.js`). Do **not** rely on `../` in `include` — entries like `../lib/foo.py` break imports in the container.

### Import style in Python functions

- Import **sibling modules** bundled in the same directory: `from outreach import resolve_seller_listing`, `import draft`.
- Do **not** use `sys.path` hacks or `from some_parent_package.module import …` unless that package is also listed in `include` and laid out as importable paths in the zip.
- Shared code in a monorepo: keep sources one level up and add **symlinks** in the function dir (e.g. `outreach.py -> ../outreach.py`) and list the symlink name in `include`.

### Node functions

- Build to `dist/tsc/` (or similar) and set `entrypoint: dist/tsc/index.js`.
- `include: [dist/tsc/**]` plus commit built output, or build in CI before deploy.
- Dependencies belong in **`package.json`** at the function root, not only at repo root.

---

## `.edufc.yml` checklist

1. `apiRevision: edurata.io/function/v1` on new functions.
2. `name` unique and stable (registry / deployments reference it).
3. `interface.inputs` / `interface.outputs` match what `handler` returns.
4. `requirements.txt` or `package.json` present when using third-party libs.
5. `include` lists every non-vendored `.py` / `.js` file the handler imports.
6. Env secrets declared as `type: env` in inputs (e.g. `AIRTABLE_API_KEY`).

---

## Referencing from workflows

```yaml
my-step:
  source:
    repoUrl: https://github.com/Edurata/edurata-functions.git
    path: general/axios
  props:
    method: GET
    url: https://api.example.com/data
    headers:
      Authorization: Bearer ${secrets.MY_TOKEN}
```

Private/customer functions use the same contract from `edurata-workflows-private` (or another git repo).

---

## Anti-patterns

- Parent-package imports (`from kleinanzeigen.scraper import …`) without bundling that package into the zip.
- `include: ../*.py` or other paths that produce `..` segments in the zip.
- Missing `requirements.txt` / `package.json` while importing `requests`, `axios`, etc.
- Hand-editing files under `dist/` without updating `src/` and rebuilding (Node).

---

## Related repos

| Repo | Role |
| --- | --- |
| `edurata-workflows` | Public workflow examples consuming these functions |
| `edurata-workflows-private` | Customer workflows + co-located private functions (e.g. Kleinanzeigen) |
| `edurata-yaml` | JSON schema for `.edufc.yml` / `.eduwc.yml` |
