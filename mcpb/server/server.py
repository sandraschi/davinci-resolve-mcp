'''MCP server entry point for DaVinci Resolve MCP.

This is the MCPB-compliant server wrapper that launches the DaVinci Resolve MCP server.
'''

import sys
from pathlib import Path

# Add parent directory to path to import main server
parent_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(parent_dir))

# Import and run main server
try:
    from server import main
except ImportError:
    try:
        from davinci_resolve_mcp.server import main
    except ImportError:
        import davinci_resolve_mcp
        main = davinci_resolve_mcp.main

if __name__ == '__main__':
    main()

