"""CORS konfiguráció egységtesztjei."""

from src.main import _allowed_origins


class TestCorsOrigins:
    def test_default_origin_is_localhost_3000(self, monkeypatch):  # type: ignore[no-untyped-def]
        """Alapértelmezett engedélyezett origin: localhost:3000."""
        monkeypatch.delenv("SWISSPM_CORS_ORIGINS", raising=False)
        assert _allowed_origins() == ["http://localhost:3000"]

    def test_origins_from_env_comma_separated(self, monkeypatch):  # type: ignore[no-untyped-def]
        """Env-ből vesszővel tagolt lista, whitespace levágva."""
        monkeypatch.setenv(
            "SWISSPM_CORS_ORIGINS",
            "http://localhost:3310, http://127.0.0.1:3310 ,",
        )
        assert _allowed_origins() == [
            "http://localhost:3310",
            "http://127.0.0.1:3310",
        ]

    def test_empty_env_falls_back_to_default(self, monkeypatch):  # type: ignore[no-untyped-def]
        """Üres env érték → alapértelmezés."""
        monkeypatch.setenv("SWISSPM_CORS_ORIGINS", "  ")
        assert _allowed_origins() == ["http://localhost:3000"]
