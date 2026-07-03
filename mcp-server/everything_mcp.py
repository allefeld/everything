"""MCP server wrapping the 'everything' toolkit (etext / rg --pre etext)."""

import json
import shutil
import subprocess
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("everything")


def _etext() -> str:
    """Resolve the etext executable from PATH, raising if absent."""
    cmd = shutil.which("etext")
    if cmd is None:
        raise RuntimeError(
            "etext not found on PATH. "
            "Copy etext to a directory on your PATH (e.g. ~/.local/bin/) "
            "as described in the everything project README."
        )
    return cmd


@mcp.tool()
def search(
    pattern: str,
    path: str,
    ignore_case: bool = False,
    glob: Optional[str] = None,
    max_count: Optional[int] = None,
) -> str:
    """Search file contents across all supported file types using etext as a preprocessor.

    Invokes `rg --pre etext` so PDFs, Office documents, ebooks, images, archives,
    and other non-text files are converted to Markdown before being searched.
    Line numbers in results refer to positions in the converted Markdown, not the
    original file; use fetch() to read the full converted content.

    Args:
        pattern: Ripgrep regex pattern to search for.
        path: File or directory to search (absolute or ~ paths accepted).
        ignore_case: Case-insensitive matching (-i).
        glob: Filename glob filter applied before searching, e.g. "*.pdf".
        max_count: Maximum number of matches returned per file.
    """
    path = str(Path(path).expanduser().resolve())

    cmd = ["rg"]
    if ignore_case:
        cmd.append("-i")
    if glob:
        cmd.extend(["--glob", glob])
    if max_count is not None:
        cmd.extend(["--max-count", str(max_count)])
    cmd.extend(["--pre", _etext(), "--json", "--", pattern, path])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 2:
        return f"ripgrep error:\n{result.stderr.strip()}"

    hits = []
    for line in result.stdout.splitlines():
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "match":
            continue
        data = obj["data"]
        path_field = data["path"]
        hit_path = path_field.get("text") or path_field.get("bytes", "(binary path)")
        line_text = data["lines"].get("text", "").rstrip("\n")
        hits.append({"file": hit_path, "line": data["line_number"], "text": line_text})

    if not hits:
        return "No matches found."

    lines = [f"{h['file']}:{h['line']}: {h['text']}" for h in hits]
    return f"{len(hits)} match(es).\n\n" + "\n".join(lines)


@mcp.tool()
def fetch(file: str) -> str:
    """Convert a file to Markdown text using etext.

    Handles PDFs, Office documents (.docx, .odt, .pptx, .ppt, …), ebooks
    (.epub, .mobi, .djvu, …), HTML, images (JPEG, PNG, WebP, SVG, …),
    audio files, and compressed archives. Results are cached on disk so
    repeated calls for the same file are fast.

    Args:
        file: Path to the file to convert (absolute or ~ paths accepted).
    """
    file = str(Path(file).expanduser().resolve())

    result = subprocess.run(
        [_etext(), file], capture_output=True, text=True, timeout=120
    )

    content = result.stdout
    stderr = result.stderr.strip()

    if result.returncode != 0:
        msg = f"etext exited {result.returncode}"
        if stderr:
            msg += f"\n{stderr}"
        if content:
            msg += f"\n\n(partial output)\n{content}"
        return msg

    if not content:
        return "(etext produced no output)" + (f"\n{stderr}" if stderr else "")

    if stderr:
        return f"[etext warnings]\n{stderr}\n\n[content]\n{content}"

    return content


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
