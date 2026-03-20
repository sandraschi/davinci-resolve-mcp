"""
Run the HTTP API server for the SOTA webapp only.
Use: python -m davinci_resolve_mcp.run_api --port 10843 --host 127.0.0.1
Avoids RuntimeWarning from running server.py as __main__ (double-import).
"""
import argparse
import os
import sys

from .server import initialize_server, start_server

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DaVinci Resolve MCP API server for webapp")
    parser.add_argument("--host", type=str, help="Host to bind to (overrides HOST env var)")
    parser.add_argument("--port", type=int, help="Port to listen on (overrides PORT env var)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--config", type=str, help="Path to configuration file")
    args = parser.parse_args()

    if args.host:
        os.environ["HOST"] = args.host
    if args.port:
        os.environ["PORT"] = str(args.port)
    if args.debug:
        os.environ["DEBUG"] = "true"
    if args.config:
        os.environ["CONFIG_PATH"] = args.config

    try:
        initialize_server()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Server init warning (Resolve may be unavailable): %s", e)

    try:
        start_server()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Server error: %s", e)
        sys.exit(1)
