"""
Configuration management for Binance PortfolioPulse AI.
Loads settings from environment variables and .env file with zero-dependency fallback.
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def load_env_file(filepath: Path) -> None:
    """Fallback .env parser if python-dotenv is not installed."""
    if not filepath.exists():
        return
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("\"'")
                if key not in os.environ:
                    os.environ[key] = val
    except Exception:
        pass


# Attempt to load dotenv
env_path = Path(__file__).resolve().parent.parent / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=env_path)
except ImportError:
    load_env_file(env_path)


@dataclass
class AgentConfig:
    """Application and Risk Configuration."""
    mode: str = os.getenv("AGENT_MODE", "mock").lower()
    
    # Binance Agent OS MCP Server
    mcp_endpoint: str = os.getenv(
        "BINANCE_MCP_ENDPOINT", "https://agent.binance.com/mcp/agentic"
    )
    mcp_auth_token: Optional[str] = os.getenv("BINANCE_MCP_AUTH_TOKEN", None)
    
    # Binance REST Exchange API
    api_key: Optional[str] = os.getenv("BINANCE_API_KEY", None)
    api_secret: Optional[str] = os.getenv("BINANCE_API_SECRET", None)
    base_url: str = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
    
    # Quantitative Risk Thresholds
    risk_concentration_threshold: float = float(
        os.getenv("RISK_CONCENTRATION_THRESHOLD", "0.35")
    )
    risk_volatility_threshold: float = float(
        os.getenv("RISK_VOLATILITY_THRESHOLD", "0.08")
    )
    min_stablecoin_buffer: float = float(
        os.getenv("MIN_STABLECOIN_BUFFER", "0.10")
    )
    
    # Output and AI Options
    output_dir: str = os.getenv("REPORTS_OUTPUT_DIR", "reports")
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", None)


config = AgentConfig()
