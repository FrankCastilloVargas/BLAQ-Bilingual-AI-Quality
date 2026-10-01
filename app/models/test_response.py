from pydantic import BaseModel, Field


class TestResponseUpdate(BaseModel):
    actual_response: str = Field(min_length=1)
