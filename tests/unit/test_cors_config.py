"""CORS konfiguráció egységtesztjei."""

from src.main import _allowed_origins


class TestCorsOrigins:
    def test_default_origins_include_3000_and_3310(self, monkeypatch):  # type: ignore[no-untyped-def]
        """Alapértelmezett engedélyezett originek: localhost:3000, 3310, 3410 és 127.0.0.1."""
        monkeypatch.delenv("SWISSPM_CORS_ORIGINS", raising=False)
        origins = _allowed_origins()
        assert "http://localhost:3000" in origins
        assert "http://localhost:3310" in origins
        assert "http://localhost:3410" in origins
        assert "http://127.0.0.1:3410" in origins

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
        origins = _allowed_origins()
        assert "http://localhost:3310" in origins
