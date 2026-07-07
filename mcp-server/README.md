# everything MCP server

An MCP server that wraps the `everything` toolkit, letting Claude search and
read the contents of arbitrary files on this machine without reimplementing any
of the conversion tooling.

## Tools

### `list_dir(path)`

Lists the contents of a directory (one level, non-recursive). Returns each
entry's name, type (file or dir), and size in bytes for files. Directories
are listed first.

- **path** — Directory to list (absolute, or `~/…`-relative).

### `search(pattern, path, [ignore_case, glob, max_count, context, before, after])`

Runs `rg --pre etext` to search inside PDFs, Office documents, ebooks, archives,
HTML, images, and other file types that `etext` can convert.

- **pattern** — Ripgrep regex.
- **path** — File or directory to search (absolute, or `~/…`-relative).
- **ignore_case** — Case-insensitive matching (`-i`). Default `false`.
- **glob** — Filename glob filter, e.g. `"*.pdf"`. Optional.
- **max_count** — Maximum matches returned per file. Optional.
- **context** — Lines of context to show before and after each match (`-C`).
  Overrides `before`/`after` if set. Optional.
- **before** — Lines of context before each match (`-B`). Optional.
- **after** — Lines of context after each match (`-A`). Optional.

Returns matches as `file:line: text`, with context lines as `file-line- text`
and `--` separating non-adjacent match regions within the same file. Line
numbers refer to positions in the converted Markdown output, not the original
file.

### `fetch(file, [start, end])`

Runs `etext <file>` (stdout mode) and returns the full converted Markdown,
using the on-disk cache at `~/.cache/everything/` if the file has been
converted before. Use `start`/`end` to retrieve only a section when a full
fetch would exceed the tool result size limit.

- **file** — Path to the file to convert. Absolute or `~/…`-relative.
- **start** — First line to return, 1-based inclusive. Optional.
- **end** — Last line to return, 1-based inclusive. Optional.

When a line range is given, the result begins with a `[Lines X–Y of N]`
header. Line numbers from `search` results can be used directly.

## Requirements

All conversion tools (`etext`, `rg`, Pandoc, LibreOffice, Calibre, etc.) must
be installed on the host and `etext` must be on your `PATH`. See the
[project README](../README.md) for the full list and installation instructions.

## Installation

Install the MCP server with `uv` or `pipx` directly from the GitHub repository:

```bash
uv tool install 'git+https://github.com/allefeld/everything.git#subdirectory=mcp-server'
```

```bash
pipx install 'git+https://github.com/allefeld/everything.git#subdirectory=mcp-server'
```

This installs the `everything-mcp` executable into your tool PATH
(`~/.local/bin/` for both `uv tool` and `pipx`).

To update to the latest version:

```bash
uv tool upgrade everything-mcp
pipx upgrade everything-mcp
```

## Configuring Claude Desktop / Cowork

Once installed, register the server by adding it to your MCP configuration.

**Claude Desktop** — `~/.config/Claude/claude_desktop_config.json` (Linux) or
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "everything": {
      "command": "everything-mcp"
    }
  }
}
```

**Claude Code / Cowork** — add to `.claude/mcp.json` in a project root, or
`~/.claude/mcp.json` for a global registration:

```json
{
  "mcpServers": {
    "everything": {
      "type": "stdio",
      "command": "everything-mcp"
    }
  }
}
```

If `~/.local/bin/` is not on the PATH seen by Claude Desktop (common on macOS
where the app may not inherit your shell's PATH), use the full path.

***

This software is copyrighted © 2026 by Carsten Allefeld and released under the terms of the GNU General Public License, version 3 or later.
