# SysClean Web UI

React + Vite dashboard for SysClean — monitors the execution queue, rollback history, and system health, talking to the FastAPI backend in `python/web/`.

## Development

```bash
npm install
npm run dev      # start the dev server with HMR
npm run lint      # run ESLint
npm run build      # production build
npm run preview     # preview the production build locally
```

By default the app expects the SysClean daemon's API to be reachable locally (see `python/web/server.py`). Start the backend first, or run `sysclean ui` from the repo root to launch both.
