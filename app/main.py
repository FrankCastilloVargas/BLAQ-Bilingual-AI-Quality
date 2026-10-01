from fastapi import FastAPI

from app.api.audits import router as audits_router
from app.api.evaluations import router as evaluations_router

app = FastAPI(
    title="BLAQ — Bilingual Language & AI Quality",
    version="0.1.0",
    description="Human-in-the-loop bilingual AI quality evaluation API.",
)

app.include_router(audits_router, prefix="/audits", tags=["audits"])
app.include_router(evaluations_router, prefix="/evaluations", tags=["evaluations"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
