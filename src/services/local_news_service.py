"""SPEC-047 source-safe local news."""

from pydantic import BaseModel, Field


class LocalNewsResponse(BaseModel):
    postcode: str = Field(pattern=r"^\d{4}$")
    items: list[dict[str, object]]
    status: str


class LocalNewsService:
    def get_local(self, postcode: str) -> LocalNewsResponse:
        return LocalNewsResponse(postcode=postcode, items=[], status="source_pending")
