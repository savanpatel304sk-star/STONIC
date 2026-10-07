# STONIC — working assistant source

This folder is a runnable Python project assembled from the supplied STONIC screenshot and the directory layout in chat. The actual `E:\stonic` drive is not accessible from this Linux workspace; the source is under `/home/user/stonic` and can be copied to `E:\stonic` on Windows.

## Run from source (Windows 10/11)

1. Install Python 3.10 or newer.
2. Open this folder and run `run_stonic.bat`, or use:

```bat
python -m pip install -r requirements.txt
python bootstrap.py
```

The local service binds to `127.0.0.1` by default and opens the STONIC interface in the default browser. Run diagnostics with:

```bat
python bootstrap.py --diagnose
```

The browser and local tools operate on the PC that runs `bootstrap.py`. In an Arena preview, they operate on the preview sandbox instead.

## Configure AI

Copy `.env.example` to `.env` in this source folder and set `OPENAI_API_KEY` and `AI_MODEL`. Do not commit `.env`. The key stays in the Python process and is not put in browser storage or logs. If it is missing or the provider is unreachable, STONIC reports AI OFFLINE/error; it does not invent a response. The current provider implementation supports OpenAI-compatible Chat Completions only.

## Make a Windows portable folder / executable

On a Windows PC, run `build_exe.bat`. It creates `dist\STONIC\STONIC.exe` with its required adjacent files. Keep the whole `dist\STONIC` folder together. This is a portable folder build, not a claim that every dependency can be embedded into one file. A Windows GitHub Actions workflow is also provided in `.github/workflows/windows-build.yml`.

**This workspace is Linux, so a native Windows EXE has not been built or run here.** The batch file and Windows CI workflow are prepared for a real Windows build; do not treat a Linux binary as a Windows executable.

## Implemented and connected

- Screenshot-based blue glass STONIC interface, shared Home/Assistant chat, Tools and Settings views.
- Shared conversation service, SSE streaming provider, safe command router and tool registry.
- Lazy browser, filesystem and Windows/system specialist agents, task planner, task records, result checks, permissions and event bus.
- Real CPU/RAM/disk readings (`psutil` with a Linux fallback), host/network status and diagnostics.
- SQLite user-approved memory; credential-like memories are rejected. Basic memory lookup works without an API key.
- Allow-listed browser URL/search actions, Downloads open/create-folder actions and Calculator launch. No arbitrary model-generated shell commands.
- Micro-agent registry is lazy: it can register real plugins as they are added. No hundreds of empty `agent_001.py` files are generated or loaded.
- Browser Web Speech APIs provide push-to-talk STT, browser TTS, voice toggle and optional wake phrase when the browser supports them and microphone permission is granted.
- An official WhatsApp Cloud API connector can send a user-entered E.164 recipient/message only after explicit confirmation; the API message ID is checked. It needs credentials and does not resolve contact names or provide an inbound webhook in this build.
- Local logging, `.env.example`, tests and a PyInstaller Windows build script.

## Not supplied / not claimed

- The screenshot provides a **rendered character image**, not a GLB/GLTF model. The scene is preserved visually but there is no real 3D model/rig in this package.
- WhatsApp requires official Cloud API credentials. There is no contact-name resolver or inbound webhook endpoint; without credentials it remains offline and does not send.
- The listed finance, vision/OCR, email, calendar, social, media and hundreds of numbered micro-agent modules are not implemented as empty placeholders. Extend them as real plugins through the lazy registry and permission/tool contracts.
- Microphone and speaker behavior depends on the local browser/OS. It was not hardware-tested in this Linux sandbox.

## Project layout (implemented core)

```text
stonic/
├── launcher.py, main.py, bootstrap.py, startup.py
├── config.py, requirements.txt, pyproject.toml, .env.example
├── core/                 event bus, planner, permissions, state, orchestrator
├── intelligence/         intent analysis and action verification
├── orchestration/        shared task router and agent registry API
├── agents/               lazy browser, file and system agents
├── micro_agents/         dynamic lazy plugin registry
├── memory/               SQLite memory
├── tools/                command parser, safe tool registry and system metrics
├── services/             assistant, AI provider and HTTP service
├── voice/                browser speech capability bridge
├── safety/               permission policy exports
├── ui/web/               supplied-reference STONIC frontend and assets
└── tests/                 unit and integration checks
```
