import argparse
import os
from mcp_tools_loader import generate_tools_from_multiple_mcp_binaries, list_mcp_tools

def list_tools_command(binary_paths: list, include: list, exclude: list, use_cache: bool):
    tools = generate_tools_from_multiple_mcp_binaries(binary_paths, include, exclude, use_cache)
    for tool_func in tools:
        print(f"- {tool_func.__name__}: {tool_func.__doc__}")

def main():
    parser = argparse.ArgumentParser(description="MCP Tools Loader CLI")
    parser.add_argument(
        "command", choices=["list"], help="Command to run: 'list' for listing tools"
    )
    parser.add_argument(
        "binaries", nargs="+", help="Paths to the MCP tool binaries"
    )
    parser.add_argument(
        "--include", nargs="*", default=[], help="Regex patterns to include specific tools"
    )
    parser.add_argument(
        "--exclude", nargs="*", default=[], help="Regex patterns to exclude tools"
    )
    parser.add_argument(
        "--no-cache", action="store_true", help="Disable caching"
    )

    args = parser.parse_args()

    if args.command == "list":
        use_cache = not args.no_cache
        list_tools_command(args.binaries, args.include, args.exclude, use_cache)

if __name__ == "__main__":
    main()
