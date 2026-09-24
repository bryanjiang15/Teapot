<p align="center">
  <img src="docs/media/teapot-banner.svg" alt="Teapot — Brew your own game. Visual rules, reusable components, Python runtime." width="100%">
</p>

<p align="center">
  <a href="#quickstart">Get started</a> ·
  <a href="#see-it-in-action">Watch the editor</a> ·
  <a href="#architecture">Explore the architecture</a> ·
  <a href="https://github.com/bryanjiang15/Teapot/issues">Report an issue</a>
</p>

# Teapot

**Build the rules. Shape the board. Make the game yours.**

Teapot is an experimental toolkit for developers and tabletop game designers building custom trading card and board games. Its React workspace combines visual rule graphs and scene composition with a Python backend, AI-assisted compilation, and a reusable game runtime. The goal: let designers iterate on game-specific rules without rebuilding an engine for every idea.

> **Development status:** The editor, project API, compilation pipeline, and script-based runtime are implemented in this repository. They are still being integrated. The workspace chat uses placeholder responses; hosted multiplayer, Unity integration, and AI playtesting are not a completed end-to-end experience. The frontend production build currently has TypeScript errors—see [FAQ](#faq).

## Contents

- [See it in action](#see-it-in-action)
- [Features](#features)
- [Quickstart](#quickstart)
- [Usage examples](#usage-examples)
- [Architecture](#architecture)
- [Repository map](#repository-map)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Credits and resources](#credits-and-resources)

## See it in action

### Make behavior visible

Add rule nodes and arrange them on the canvas. The graph makes triggers, effects, and their relationships easier to inspect than a long rules document.

![Adding and arranging rule nodes in the Teapot editor](docs/images/react-app.png)

### Compose the game surface

Switch to the Scene tab to expand a component's hierarchy, add nested slots, and inspect the composition with pan and zoom.

![Editing a component composition in the Teapot scene editor](docs/images/workspace.png)


## Features

| Capability | What it gives you |
| --- | --- |
| **Visual rule authoring** | React Flow nodes for triggers, state, input, branching, and effects; each component owns its graph. |
| **Scene composition** | A PixiJS canvas and hierarchy for slots, sprites, text, and references to other components. |
| **Project persistence** | Authenticated project/component endpoints backed by PostgreSQL; the editor attempts autosave after two seconds of inactivity. |
| **AI-assisted compilation** | A backend pipeline analyzes game context and component graphs, generates Python scripts, resolves subscriptions, and validates the assembled ruleset. Requires an OpenAI API key for model calls. |
| **Reusable Python runtime** | `RulesetLoader` validates compiled data; `MatchActor` coordinates lifecycle hooks, an event stack, state changes, and player input. An explicit RNG seed supports reproducible randomness. |

## Quickstart

### Prerequisites

- **Python 3.11+** and Git.
- **Node.js 22.12+** and npm for the Vite 7 frontend.
- **PostgreSQL**; the commands below use Docker to start a local PostgreSQL 16 database.
- An **OpenAI API key** only when invoking AI compilation. Basic project editing does not need model calls.

These instructions target local development in Bash (macOS, Linux, or WSL). Redis and the separate `CreatorAPI` service are not needed for the project editor path below.

### 1. Clone and install Python dependencies

```bash
git clone https://github.com/bryanjiang15/Teapot.git
cd Teapot
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pydantic-settings email-validator 'bcrypt==4.0.1'
```

The extra packages cover imports absent from `requirements.txt`; the bcrypt pin keeps local password hashing compatible with the repository's Passlib integration.

### 2. Start a development database

```bash
docker run --name teapot-postgres \
  -e POSTGRES_USER=teapot \
  -e POSTGRES_PASSWORD=teapot_dev \
  -e POSTGRES_DB=tcg_db \
  -p 5432:5432 \
  -v teapot-pgdata:/var/lib/postgresql/data \
  -d postgres:16

docker exec teapot-postgres pg_isready -U teapot -d tcg_db
```

Wait until the final command reports that PostgreSQL is accepting connections. These credentials are for local development.

### 3. Configure and launch the API

Run from the repository root:

```bash
cd TeapotAPI
python - <<'PY'
from pathlib import Path
import secrets

path = Path('.env')
if path.exists():
    print('Keeping existing .env; check DATABASE_URL and SECRET_KEY.')
else:
    path.write_text(
        'DATABASE_URL=postgresql+asyncpg://teapot:teapot_dev@localhost:5432/tcg_db\n'
        f'SECRET_KEY={secrets.token_urlsafe(48)}\n'
        'ENVIRONMENT=development\n'
        'DEBUG=true\n'
    )
PY
python run.py
```

On a fresh database, API startup creates tables from the ORM models. Existing databases may require the migrations in `TeapotAPI/alembic/`; startup does not migrate existing tables. Keep `.env` out of version control.

Open [API documentation](http://localhost:8000/docs), or check the server from a second terminal:

```bash
curl http://localhost:8000/health
```

Expected fields include `"status":"healthy"` and `"environment":"development"`. The health endpoint reports application status; it is not a full dependency readiness check.

### 4. Launch the frontend

In another terminal, from the repository root:

```bash
cd frontend
npm ci
npm run dev
```

Open the URL Vite prints, normally [http://localhost:5173](http://localhost:5173). Register an account, sign in, then create a project from the dashboard. The frontend defaults to `http://localhost:8000`; set `VITE_API_URL` in `frontend/.env.local` if your API uses another address, then restart Vite.

**Verification scope:** `npm ci` and Vite startup were checked at commit `a2e54e7`; editor interactions were captured with local API fixtures. Database setup, authentication, and AI compilation were reviewed against source but were not exercised end to end. `npm run build` currently fails on existing TypeScript issues.

## Usage examples

### Create your first component

1. Open a project and expand the project dropdown above the canvas.
2. Use **Add component**, then select the component you want to edit.
3. In **Node**, choose **Trigger → On game started (lifecycle)** and **Function → Effect**. Arrange the nodes, connect their execution ports, and describe the effect's behavior.
4. In **Scene**, use **Add slot** to start a composition; use the hierarchy to add children and the canvas to select, pan, and zoom through the composition.
5. Allow autosave to finish before leaving. A save error means the backend has not confirmed your changes.

### Compile a saved project and export its ruleset

Use the email/password account created above. The login route accepts JSON, not an OAuth form. Run this from the repository root with the virtual environment active:

```bash
python - <<'PY'
import getpass
import json
from pathlib import Path
import httpx

with httpx.Client(base_url='http://localhost:8000', timeout=300) as client:
    login = client.post('/auth/login', json={
        'email': input('Email: '),
        'password': getpass.getpass('Password: '),
    })
    login.raise_for_status()
    client.headers['Authorization'] = f"Bearer {login.json()['access_token']}"
    project_id = input('Project UUID from the workspace URL: ').strip()
    compiled = client.post(f'/projects/{project_id}/compile')
    compiled.raise_for_status()
    print(json.dumps(compiled.json(), indent=2))
    if compiled.json().get('failed'):
        raise SystemExit('Resolve failed components before exporting.')
    response = client.get(f'/projects/{project_id}/ruleset')
    response.raise_for_status()
    Path('ruleset.json').write_text(json.dumps(response.json(), indent=2))
PY
```

Before invoking compilation, export `OPENAI_API_KEY` in the API server's shell and restart the server. Model calls can incur charges. Review the compilation report and generated scripts: the pipeline can fall back to template compilation, so an HTTP success alone does not establish correct game behavior.

### Load the export into Python

From the repository root, using the `ruleset.json` exported above:

```python
import json
from pathlib import Path
from TeapotEngine import MatchActor, RulesetLoader

ruleset = RulesetLoader().from_api_response(
    json.loads(Path('ruleset.json').read_text())
)
match = MatchActor(
    match_id='local-demo',
    ruleset=ruleset,
    player_ids=['alice', 'bob'],
    seed=42,
)
result = match.begin_game()
print(result)
```

This starts the runtime using the behavior in your compiled components. A host application must handle subsequent player input and presentation; this snippet is not a complete game client.

## Architecture

The editor stores authoring data. Compilation turns that data into a ruleset that a separate Python host can load into the runtime.

```mermaid
flowchart TD
    UI["React workspace"] -->|"JWT-authenticated HTTP"| API["FastAPI: auth and projects"]
    API <-->|"SQLAlchemy: projects and components"| DB[("PostgreSQL")]
    API -->|"POST project compile"| CP["Game compilation pipeline"]
    CP <-->|"Agent model calls"| AI["OpenAI API"]
    CP -->|"Scripts and metadata"| API
    API -->|"GET project ruleset"| HOST["Python host: RulesetLoader"]
    HOST --> MATCH["MatchActor"]
    MATCH <-->|"Resolve emitted events"| EVENTS["Event stack and EventBus"]
    MATCH -->|"Lifecycle hooks"| RUNNER["ScriptRunner and GameAPI"]
    RUNNER -->|"Property and object changes"| STATE["GameState"]
```

**Runtime boundary:** the host explicitly loads the exported ruleset; the diagram does not imply a deployed multiplayer service. `CreatorAPI/` is a separate ability-generation experiment. The current workspace chat is not wired to it.

**Script execution:** `ScriptRunner` restricts AST constructs and builtins. This is not an operating-system isolation boundary; review generated scripts before running them, and do not treat this prototype as a host for untrusted public code.

## Repository map

| Path | Start here when you want to… |
| --- | --- |
| [`frontend/`](frontend/) | Work on React, Redux, React Flow, and PixiJS editor interactions. |
| [`TeapotAPI/app/api/`](TeapotAPI/app/api/) | Inspect authentication, project persistence, compilation, and ruleset routes. |
| [`TeapotAPI/app/services/compiler/`](TeapotAPI/app/services/compiler/) | Trace graph/scene processing and the multi-stage agent pipeline. |
| [`TeapotEngine/`](TeapotEngine/) | Embed the current script-based game runtime. |
| [`TeapotEngine-block/`](TeapotEngine-block/) | Explore the earlier block/interpreter implementation and its tests. |
| [`CreatorAPI/`](CreatorAPI/) | Explore the separate natural-language ability-generation pipeline. |

## FAQ

<details>
<summary><strong>Why does development mode start while the production build fails?</strong></summary>

Vite development mode transpiles the frontend, while `npm run build` runs TypeScript checking first. At the reviewed commit, the locked TypeScript 5.6 version rejects `erasableSyntaxOnly`, and the source also contains graph/scene typing errors and unused declarations. Updating TypeScript alone will not resolve all of these. Treat this as a development prototype until the build is repaired.

</details>

<details>
<summary><strong>Why does the AI chat only acknowledge my message?</strong></summary>

`AIAssistant.tsx` currently simulates replies with a timer. Backend compilation is a separate implemented path, available through `POST /projects/{project_id}/compile`; the chat panel does not invoke it.

</details>

<details>
<summary><strong>Why do registration or API startup fail after installing requirements?</strong></summary>

Check that the virtual environment is active and the extra packages in step 1 are installed. `pydantic-settings` supplies API configuration, `email-validator` supports the email schemas, and the bcrypt pin avoids compatibility problems with Passlib. Run the API from `TeapotAPI/` so it reads the intended `.env`; verify PostgreSQL is accepting connections.

</details>

<details>
<summary><strong>Why did a reload lose my edits?</strong></summary>

The editor saves through the project API, not browser-only storage. Check the save status, API process, database connection, and token validity. The unload save is best effort; wait for the normal save to complete before closing the page. If your session expired, sign in again.

</details>

<details>
<summary><strong>Why does <code>python example.py</code> fail?</strong></summary>

The root example still imports modules from an older engine layout, including `TeapotEngine.core.Engine`. Use the `RulesetLoader` and `MatchActor` example above for the current runtime; `TeapotEngine-block/` contains the earlier implementation.

</details>

<details>
<summary><strong>Docker says the database container already exists. What next?</strong></summary>

For the container created by this guide, run `docker start teapot-postgres` instead of repeating `docker run`. If port 5432 is already in use, use your existing PostgreSQL instance or choose another host port and update `DATABASE_URL` accordingly.

</details>

## Contributing

Open an [issue](https://github.com/bryanjiang15/Teapot/issues) with the intended behavior, reproduction steps, and relevant logs before a substantial change. Keep pull requests focused and include a screenshot or short recording for editor changes.

For frontend changes:

```bash
cd frontend
npm test
npm run lint
npm run build
```

Report any existing failures separately from those introduced by your change. Useful contributions include fixing the production build, completing chat/backend integration, updating the legacy example, and documenting full compile-to-runtime workflows.

## Credits and resources

Created in [bryanjiang15/Teapot](https://github.com/bryanjiang15/Teapot), using React, Redux Toolkit, React Flow, PixiJS, FastAPI, SQLAlchemy, PostgreSQL, and the OpenAI Agents SDK.

- [Frontend source and notes](frontend/)
- [Backend documentation](TeapotAPI/docs/README.md) — some roadmap material predates the current editor.
- [Current runtime exports and usage](TeapotEngine/__init__.py)
- [Compiler implementation](TeapotAPI/app/services/compiler/game_compilation_pipeline.py)

No root license file was present at the reviewed commit. Ask the maintainer about reuse terms before redistributing the project.
