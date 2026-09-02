"""SPEC-046 vote analysis."""

from pydantic import BaseModel, Field


class Poll(BaseModel):
    institute: str
    sample_size: int = Field(gt=0)
    margin_percent: float = Field(gt=0)
    yes_percent: float = Field(ge=0, le=100)
    fieldwork_date: str


class Proposal(BaseModel):
    id: int
    title: str
    vote_date: str
    status: str
    source: str = "Bundeskanzlei / BFS VoteInfo"


class Analysis(BaseModel):
    proposal: Proposal
    pro_arguments: list[str]
    contra_arguments: list[str]
    polls: list[Poll]
    local_yes_percent: float | None
    cantonal_yes_percent: float | None
    national_yes_percent: float | None


class VoteAnalysisService:
    def proposals(self) -> list[Proposal]:
        return [
            Proposal(
                id=6670, title="13. AHV-Rente", vote_date="2024-03-03", status="final"
            ),
            Proposal(
                id=6801,
                title="Kommende eidgenössische Vorlage",
                vote_date="2026-11-29",
                status="upcoming",
            ),
        ]

    def analysis(self, i: int) -> Analysis | None:
        p = next((x for x in self.proposals() if x.id == i), None)
        if not p:
            return None
        final = p.status == "final"
        polls = (
            []
            if final
            else [
                Poll(
                    institute="Demo Institut",
                    sample_size=1200,
                    margin_percent=2.8,
                    yes_percent=52,
                    fieldwork_date="2026-08-20",
                )
            ]
        )
        return Analysis(
            proposal=p,
            pro_arguments=["Offizielle Pro-Argumente"],
            contra_arguments=["Offizielle Contra-Argumente"],
            polls=polls,
            local_yes_percent=61.2 if final else None,
            cantonal_yes_percent=59.8 if final else None,
            national_yes_percent=58.2 if final else None,
        )
