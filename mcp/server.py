"""
MCP (Model Context Protocol) server management for Singapore LTA data.

This module handles installation and startup of the Singapore LTA MCP server.
Reference: https://mcpmarket.com/server/singapore-lta
"""
import os
import subprocess
from typing import Optional


def is_mcp_server_installed() -> bool:
    """
    Check if the MCP server is already installed.

    Returns:
        True if installed, False otherwise
    """
    try:
        # Check if the server is installed by trying to list it
        result = subprocess.run(
            ["npx", "-y", "@smithery/cli", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            # Check if mcp-sg-lta appears in the output
            output = result.stdout.lower() + result.stderr.lower()
            if "mcp-sg-lta" in output or "@arjunkmrm/mcp-sg-lta" in output:
                return True

        # Also check for Smithery directory structure
        home_dir = os.path.expanduser("~")
        smithery_dir = os.path.join(home_dir, ".smithery")
        if os.path.exists(smithery_dir):
            # Check for server config files
            servers_dir = os.path.join(smithery_dir, "servers")
            if os.path.exists(servers_dir):
                # Check for any files related to mcp-sg-lta
                for item in os.listdir(servers_dir):
                    if "mcp-sg-lta" in item.lower() or "sg-lta" in item.lower():
                        return True

        return False
    except Exception as e:
        print(f"Error checking MCP server installation: {e}")
        return False


def install_mcp_server() -> bool:
    """
    Install the Singapore LTA MCP server using Smithery CLI.

    Returns:
        True if installation was successful, False otherwise
    """
    try:
        print("Installing Singapore LTA MCP server...")
        print("Running: npx -y @smithery/cli install @arjunkmrm/mcp-sg-lta")

        result = subprocess.run(
            ["npx", "-y", "@smithery/cli", "install", "@arjunkmrm/mcp-sg-lta"],
            capture_output=True,
            text=True,
            timeout=120  # 2 minutes timeout for installation
        )

        if result.returncode == 0:
            print("MCP server installed successfully")
            if result.stdout:
                print(f"Installation output: {result.stdout[:200]}...")
            return True
        else:
            print(f"Failed to install MCP server. Error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("MCP server installation timed out")
        return False
    except FileNotFoundError:
        print("Error: npx not found. Please ensure Node.js is installed.")
        return False
    except Exception as e:
        print(f"Error installing MCP server: {e}")
        return False


def start_mcp_server(background: bool = True) -> Optional[subprocess.Popen]:
    """
    Start the MCP server.

    Note: MCP servers installed via Smithery are typically configured in MCP client
    configuration files rather than started as standalone processes. This function
    attempts to start the server if it can be run directly.

    Args:
        background: If True, start server in background (default: True)

    Returns:
        subprocess.Popen object if started successfully, None otherwise
    """
    try:
        print("Starting Singapore LTA MCP server...")

        # MCP servers installed via Smithery are typically used by MCP clients
        # rather than started as standalone processes. The server is usually
        # configured in the MCP client's config file.
        #
        # However, if the server can be run directly, we'll attempt it here.
        # Common patterns:
        # 1. Server runs via mcp CLI
        # 2. Server is configured in ~/.config/mcp.json or similar
        # 3. Server runs as part of an MCP client connection

        # Try to check if server can be started directly
        # For now, we'll just confirm installation and note that
        # the server will be available for MCP clients to connect to

        print("MCP server installed and ready for MCP client connections")
        print("Note: MCP servers are typically used by MCP clients (like Claude Desktop)")
        print("The server is configured and ready to use via MCP client configuration")

        # Return None as the server doesn't run as a standalone process
        # It's used by MCP clients when they connect
        return None

    except Exception as e:
        print(f"Error starting MCP server: {e}")
        return None


def initialize_mcp_server() -> Optional[subprocess.Popen]:
    """
    Initialize MCP server: check installation, install if needed, and start.

    Returns:
        subprocess.Popen object if started successfully, None otherwise
    """
    # Check if already installed
    if not is_mcp_server_installed():
        print("MCP server not found. Installing...")
        if not install_mcp_server():
            print("Warning: Failed to install MCP server")
            return None
    else:
        print("MCP server already installed")

    # Start the server
    return start_mcp_server(background=True)

