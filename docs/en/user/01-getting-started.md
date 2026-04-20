# 01. Getting Started

## 1) Install
```bash
python -m pip install -e ".[dev]"
```

## 2) Run the server
```bash
python -m sediment_palace.main
```

The server reads JSON-RPC from `stdin` and writes responses to `stdout`.

## 3) First checks
Run, in order:
1. `initialize`
2. `tools/list`
3. `tools/call` with `healthcheck`

Expected:
- `result.data.status = "ok"`
- `result.data.service = "sediment-palace"`
