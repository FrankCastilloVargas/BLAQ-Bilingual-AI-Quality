from pydantic import BaseModel, Field


class AuditCreateFromCatalog(BaseModel):
    client: str = Field(min_length=1)
    product_name: str = Field(min_length=1)
    model_version: str | None = None
    reviewer: str = Field(min_length=1)
