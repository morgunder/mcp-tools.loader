# mcp_tools_loader.py

import subprocess
import json
from crewai_tools import tool
from typing import List

def call_mcp_tool(binary_path: str, message: dict) -> dict:
    proc = subprocess.Popen(
        [binary_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    proc.stdin.write(json.dumps(message) + "\n")
    proc.stdin.flush()
    line = proc.stdout.readline()
    return json.loads(line)

def list_mcp_tools(binary_path: str) -> List[dict]:
    return call_mcp_tool(binary_path, {"list_tools": True})["tools"]

def generate_tools_from_mcp_binary(binary_path: str, namespace: str = None):
    tools = []
    for t in list_mcp_tools(binary_path):
        tool_path = t["name"]  # e.g., linear/issues/create
        parts = tool_path.split("/")
        name_slug = "_".join(parts)
        if namespace:
            name_slug = f"{namespace}_{name_slug}"

        def make_tool_func(tool_spec, binary=binary_path):
            def _func(**kwargs):
                return call_mcp_tool(binary, {
                    "tool": tool_spec["name"],
                    "input": kwargs
                })
            _func.__name__ = f"tool_{name_slug}"
            _func.__doc__ = tool_spec.get("description", "No description.")
            return tool(tool_spec.get("description", tool_spec["name"]))(_func)

        tools.append(make_tool_func(t))
    return tools

def generate_tools_from_multiple_mcp_binaries(binaries: List[str]):
    all_tools = []
    for path in binaries:
        namespace = path.split("/")[-1].replace("-mcp", "").replace(".", "_")
        all_tools.extend(generate_tools_from_mcp_binary(path, namespace))
    return all_tools
