"""MCP server wrapping the 'everything' toolkit (etext / rg --pre etext)."""

import json
import os
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
def list_dir(path: str) -> str:
    """List the contents of a directory (one level, non-recursive).

    Returns each entry's name, type (file or dir), and size in bytes for
    files. Entries are sorted: directories first, then files, both
    case-insensitively by name.

    Args:
        path: Directory to list (absolute or ~ paths accepted).
    """
    p = Path(path).expanduser().resolve()
    if not p.exists():
        return f"Path does not exist: {p}"
    if not p.is_dir():
        return f"Not a directory: {p}"

    entries = []
    for entry in os.scandir(p):
        try:
            is_dir = entry.is_dir(follow_symlinks=True)
            size = entry.stat(follow_symlinks=True).st_size if not is_dir else None
        except OSError:
            is_dir = False
            size = None
        entries.append((entry.name, is_dir, size))

    entries.sort(key=lambda e: (not e[1], e[0].lower()))

    if not entries:
        return f"{p}/  (empty)"

    lines = [f"{p}/"]
    for name, is_dir, size in entries:
        if is_dir:
            lines.append(f"  {name}/")
        else:
            size_str = f"  [{size:,} B]" if size is not None else ""
            lines.append(f"  {name}{size_str}")

    return "\n".join(lines)


@mcp.tool()
def search(
    pattern: str,
    path: str,
    ignore_case: bool = False,
    glob: Optional[str] = None,
    max_count: Optional[int] = None,
    context: Optional[int] = None,
    before: Optional[int] = None,
    after: Optional[int] = None,
) -> str:
    """Search file contents across all supported file types using etext as a preprocessor.

    Invokes `rg --pre etext` so PDFs, Office documents, ebooks, images, archives,
    and other non-text files are converted to Markdown before being searched.
    Line numbers refer to positions in the converted Markdown; use fetch() to
    read the full converted content or a specific line range.

    Args:
        pattern: Ripgrep regex pattern to search for.
        path: File or directory to search (absolute or ~ paths accepted).
        ignore_case: Case-insensitive matching (-i).
        glob: Filename glob filter applied before searching, e.g. "*.pdf".
        max_count: Maximum number of matches returned per file.
        context: Lines of context to show before and after each match (-C).
                 Overrides `before` and `after` if set.
        before: Lines of context to show before each match (-B).
        after: Lines of context to show after each match (-A).
    """
    path = str(Path(path).expanduser().resolve())

    cmd = ["rg"]
    if ignore_case:
        cmd.append("-i")
    if glob:
        cmd.extend(["--glob", glob])
    if max_count is not None:
        cmd.extend(["--max-count", str(max_count)])
    if context is not None:
        cmd.extend(["-C", str(context)])
    else:
        if before is not None:
            cmd.extend(["-B", str(before)])
        if after is not None:
            cmd.extend(["-A", str(after)])
    cmd.extend(["--pre", _etext(), "--json", "--", pattern, path])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode == 2:
        return f"ripgrep error:\n{result.stderr.strip()}"

    # Parse JSON event stream. rg emits one begin/end block per file even
    # when context windows are non-adjacent; detect gaps to insert separators.
    file_groups = []      # [(file_path, [(line_num, is_match, text), ...])]
    current_file = None
    current_lines = []
    match_count = 0

    for raw in result.stdout.splitlines():
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        t = obj.get("type")
        if t == "begin":
            path_field = obj["data"]["path"]
            current_file = path_field.get("text") or path_field.get("bytes", "(binary)")
            current_lines = []
        elif t in ("match", "context"):
            data = obj["data"]
            is_match = t == "match"
            if is_match:
                match_count += 1
            line_text = data["lines"].get("text", "").rstrip("\n")
            current_lines.append((data["line_number"], is_match, line_text))
        elif t == "end":
            if current_file is not None and current_lines:
                file_groups.append((current_file, current_lines))
            current_file = None
            current_lines = []

    if not file_groups:
        return "No matches found."

    out = [f"{match_count} match(es).\n"]
    for file_path, group_lines in file_groups:
        out.append(f"\n--- {file_path} ---")
        prev_line_num = None
        for line_num, is_match, text in group_lines:
            # Insert separator when context windows are non-adjacent
            if prev_line_num is not None and line_num > prev_line_num + 1:
                out.append("  --")
            marker = ":" if is_match else "-"
            out.append(f"  {line_num}{marker}  {text}")
            prev_line_num = line_num

    return "\n".join(out)


@mcp.tool()
def fetch(
    file: str,
    start: Optional[int] = None,
    end: Optional[int] = None,
) -> str:
    """Convert a file to Markdown text using etext, optionally returning a line range.

    Handles PDFs, Office documents (.docx, .odt, .pptx, .ppt, …), ebooks
    (.epub, .mobi, .djvu, …), HTML, images (JPEG, PNG, WebP, SVG, …),
    audio files, and compressed archives. Results are cached on disk so
    repeated calls for the same file are fast.

    When a file's full content would exceed the tool result size limit, use
    `start`/`end` (from line numbers reported by `search`) to retrieve only
    the relevant section.

    Args:
        file: Path to the file to convert (absolute or ~ paths accepted).
        start: First line to return, 1-based inclusive. Default: 1.
        end: Last line to return, 1-based inclusive. Default: last line.
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

    # Apply line range if requested
    if start is not None or end is not None:
        all_lines = content.splitlines(keepends=True)
        total = len(all_lines)
        s = max((start - 1) if start is not None else 0, 0)
        e = min(end if end is not None else total, total)
        content = "".join(all_lines[s:e])
        header = f"[Lines {s + 1}–{e} of {total}]\n\n"
        if stderr:
            return f"[etext warnings]\n{stderr}\n\n{header}{content}"
        return header + content

    if stderr:
        return f"[etext warnings]\n{stderr}\n\n[content]\n{content}"

    return content


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
