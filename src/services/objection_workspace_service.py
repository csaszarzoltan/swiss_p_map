"""Fact-based objection workspace draft for SPEC-039."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DISCLAIMER = "Keine Rechtsberatung; ersetzt weder anwaltliche Beratung noch Vertretung. Fristen und Zuständigkeit amtlich prüfen."


class ObjectionRequest(BaseModel):
    baugesuch_id: str = Field(min_length=1, max_length=100)
    reason_category: Literal["noise", "traffic", "zoning", "heritage", "other"]
    user_notes: str = Field(max_length=4000)


class ObjectionDraft(BaseModel):
    baugesuch_id: str
    draft: str
    checklist: list[str]
    disclaimer: str = DISCLAIMER
    official_reference: str = "https://amtsblattportal.ch/"


class ObjectionWorkspaceService:
    def create(self, request: ObjectionRequest) -> ObjectionDraft:
        safe = " ".join(request.user_notes.split())
        text = f"Betreff: Baugesuch {request.baugesuch_id}\n\nSehr geehrte Damen und Herren\n\nZum publizierten Baugesuch bitte ich um Prüfung des Aspekts {request.reason_category}. Sachverhalt: {safe}\n\nFreundliche Grüsse"
        return ObjectionDraft(
            baugesuch_id=request.baugesuch_id,
            draft=text,
            checklist=[
                "Publikation und Frist prüfen",
                "Akteneinsicht klären",
                "Tatsachen und Belege kontrollieren",
                "Entwurf vor Einreichung fachlich prüfen",
            ],
        )
