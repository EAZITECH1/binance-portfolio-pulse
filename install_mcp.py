#!/usr/bin/env python3
"""
Binance PortfolioPulse AI — 1-Click Claude Desktop MCP Installer
Automatically registers the PortfolioPulse MCP server in Claude Desktop
across macOS, Windows, and Linux without manual JSON editing.
"""
import json
import os
import platform
import shutil
import sys
from pathlib import Path


def get_claude_desktop_config_path() -> Path:
    """Detects the Claude Desktop configuration file path based on the operating system."""
    system = platform.system().lower()
    home = Path.home()

    if system == "darwin":  # macOS
        return home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    elif system == "windows":  # Windows
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "Claude" / "claude_desktop_config.json"
        return home / "AppData" / "Roaming" / "Claude" / "claude_desktop_config.json"
    else:  # Linux / Unix
        return home / ".config" / "Claude" / "claude_desktop_config.json"


def install_mcp_server(uninstall: bool = False) -> bool:
    """Installs or uninstalls the PortfolioPulse server from Claude Desktop."""
    config_path = get_claude_desktop_config_path()
    repo_dir = Path(__file__).resolve().parent
    server_name = "binance-portfoliopulse"

    print("\n" + "=" * 64)
    print(" 🚀 BINANCE PORTFOLIOPULSE AI — CLAUDE DESKTOP MCP INSTALLER")
    print("=" * 64)
    print(f" 💻 Operating System: {platform.system()} ({platform.machine()})")
    print(f" 📁 Project Directory: {repo_dir}")
    print(f" ⚙️ Config Location:   {config_path}")
    print("-" * 64)

    # 1. Read existing config or start fresh
    config = {}
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            # Create a backup just in case
            backup_path = config_path.with_suffix(".json.bak")
            shutil.copy2(config_path, backup_path)
            print(f" 💾 Created backup at: {backup_path.name}")
        except Exception as e:
            print(f" ⚠️ Could not parse existing config ({e}), creating a fresh one.")
            config = {}
    else:
        config_path.parent.mkdir(parents=True, exist_ok=True)

    if "mcpServers" not in config or not isinstance(config["mcpServers"], dict):
        config["mcpServers"] = {}

    # 2. Handle Uninstall
    if uninstall:
        if server_name in config["mcpServers"]:
            del config["mcpServers"][server_name]
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2)
            print(f" 🗑️ Successfully removed '{server_name}' from Claude Desktop config.")
        else:
            print(f" ℹ️ '{server_name}' was not found in Claude Desktop config.")
        print("=" * 64 + "\n")
        return True

    # 3. Add or update PortfolioPulse MCP server definition
    python_bin = sys.executable or "python3"
    server_entry = {
        "command": python_bin,
        "args": ["-m", "src.connectors.mcp_client", "--stdio"],
        "cwd": str(repo_dir),
        "env": {
            "PYTHONPATH": str(repo_dir)
        }
    }

    config["mcpServers"][server_name] = server_entry

    # 4. Save updated configuration
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f" ❌ Failed to write config to {config_path}: {e}")
        print("=" * 64 + "\n")
        return False

    print(" ✅ Configuration updated successfully!")
    print(f"    Added '{server_name}' with 8 official Binance tools.")
    print("-" * 64)
    print(" 🎯 Next Steps:")
    print(" 1. Completely restart Claude Desktop:")
    if platform.system().lower() == "darwin":
        print("    Press Cmd + Q to quit Claude, then reopen it from Applications.")
    else:
        print("    Exit Claude Desktop from your taskbar/menu, then reopen it.")
    print(" 2. Open any chat and look for the 🔨 hammer icon showing 8 active tools!")
    print(" 3. Try asking: 'Show me top market movers and volume across the crypto watchlist'")
    print("=" * 64 + "\n")
    return True


if __name__ == "__main__":
    is_uninstall = "--uninstall" in sys.argv
    success = install_mcp_server(uninstall=is_uninstall)
    sys.exit(0 if success else 1)
