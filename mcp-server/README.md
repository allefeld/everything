# everything MCP server

An MCP server that wraps the `everything` toolkit, letting Claude search and
read the contents of arbitrary files on this machine without reimplementing any
of the conversion tooling.

## Tools

### `search(pattern, path, [ignore_case, glob, max_count])`

Runs `rg --pre etext` to search inside PDFs, Office documents, ebooks, archives,
HTML, images, and other file types that `etext` can convert.

- **pattern** — Ripgrep regex.
- **path** — File or directory to search (absolute, or `~/…`-relative).
- **ignore_case** — Case-insensitive matching (`-i`). Default `false`.
- **glob** — Filename glob filter, e.g. `"*.pdf"`. Optional.
- **max_count** — Maximum matches returned per file. Optional.

Returns one `file:line: text` line per match. Line numbers refer to positions
in the converted Markdown output, not the original file.

### `fetch(file)`

Runs `etext <file>` (stdout mode) and returns the full converted Markdown,
using the on-disk cache at `~/.cache/everything/` if the file has been
converted before.

- **file** — Path to the file to convert. Absolute or `~/…`-relative.

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

**Claude Desktop** — `~/.config/claude/claude_desktop_config.json` (Linux) or
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
where the app may not inherit your shell's PATH), use the full path:

```json
"command": "/home/ca/.local/bin/everything-mcp"
```
