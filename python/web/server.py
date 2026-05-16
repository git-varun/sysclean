"""Module docstring."""
from fastapi import FastAPI


app = FastAPI(
    title="SysClean"
)


@app.get("/health")
def health():
    """Function docstring."""

    return {
        "status": "ok"
    }
