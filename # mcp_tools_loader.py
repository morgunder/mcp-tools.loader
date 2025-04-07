import subprocess
import json
import os
import hashlib
import re
from typing import List, Optional
from crewai_tools import tool

CACHE_PATH = os.path.expanduser("~/.mcp_tool_cache.json")

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
    proc.terminate()
    return json.loads(line)

def _get_cache_key(binary_path: str) -> str:
    return hashlib.sha256(binary_path.encode()).hexdigest()

def list_mcp_tools(binary_path: str, use_cache: bool = True) -> List[dict]:
    key = _get_cache_key(binary_path)

    if use_cache and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH) as f:
            cache = json.load(f)
        if key in cache:
            return cache[key]

    tools = call_mcp_tool(binary_path, {"list_tools": True})["tools"]

    if use_cache:
        cache = {}
        if os.path.exists(CACHE_PATH):
            with open(CACHE_PATH) as f:
                cache = json.load(f)
        cache[key] = tools
        with open(CACHE_PATH, "w") as f:
            json.dump(cache, f, indent=2)

    return tools

def generate_tools_from_mcp_binary(
    binary_path: str,
    namespace: Optional[str] = None,
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    use_cache: bool = True
):
    tools = []
    all_tool_specs = list_mcp_tools(binary_path, use_cache=use_cache)

    if include:
        all_tool_specs = [t for t in all_tool_specs if any(re.search(pat, t["name"]) for pat in include)]
    if exclude:
        all_tool_specs = [t for t in all_tool_specs if not any(re.search(pat, t["name"]) for pat in exclude)]

    for t in all_tool_specs:
        parts = t["name"].split("/")
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

def generate_tools_from_multiple_mcp_binaries(
    binaries: List[str],
    include: Optional[List[str]] = None,
    exclude: Optional[List[str]] = None,
    use_cache: bool = True
):
    all_tools = []
    for path in binaries:
        namespace = os.path.basename(path).replace("-mcp", "").replace(".", "_")
        all_tools.extend(
            generate_tools_from_mcp_binary(
                path,
                namespace=namespace,
                include=include,
                exclude=exclude,
                use_cache=use_cache
            )
        )
    return all_tools
