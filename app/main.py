from fastapi import FastAPI

app = FastAPI(title="Reading List API")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}
