#!/usr/bin/env python3
"""
Binance PortfolioPulse AI — MCP Server Entrypoint
Provides clean stdio interface for Claude Desktop, Cursor, and MCP clients.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.connectors.mcp_client import run_stdio_mcp_server

if __name__ == "__main__":
    run_stdio_mcp_server()
