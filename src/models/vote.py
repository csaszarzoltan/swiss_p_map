"""Domain models for Swiss Federal votes (BFS / VoteInfo OGD) — ADR-012."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CantonVoteResult(BaseModel):
    """Result of a federal vote within a single canton."""

    canton: str = Field(..., description="Two-letter canton code (e.g. ZH, BE)")
    canton_name: str = Field(
        ..., description="Official canton name (e.g. Zürich, Bern)"
    )
    yes_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of YES votes"
    )
    no_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Percentage of NO votes"
    )
    turnout_percent: float = Field(
        ..., ge=0.0, le=100.0, description="Voter turnout percentage"
    )
    yes_count: int | None = Field(default=None, description="Absolute YES vote count")
    no_count: int | None = Field(default=None, description="Absolute NO vote count")


class FederalVoteProposal(BaseModel):
    """Swiss federal referendum proposal with national and cantonal results."""

    proposal_id: int = Field(..., description="BFS proposal ID")
    titles: dict[str, str] = Field(
        ..., description="Multilingual titles (de, en, fr, it)"
    )
    date: str = Field(..., description="Date of the vote (YYYY-MM-DD)")
    national_yes_percent: float = Field(..., ge=0.0, le=100.0)
    national_no_percent: float = Field(..., ge=0.0, le=100.0)
    national_turnout_percent: float = Field(..., ge=0.0, le=100.0)
    cantons: dict[str, CantonVoteResult] = Field(
        default_factory=dict, description="Cantonal results indexed by 2-letter code"
    )
