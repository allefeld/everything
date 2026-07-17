# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A suite of standalone bash scripts that make file contents of many types textually searchable and viewable in the terminal:

- `etext` — converts binary/rich files to Markdown text; used as a `--pre` preprocessor for `rg`
- `ecolor` — wraps `etext` and adds syntax highlighting via `bat`; used as `LESSOPEN` preprocessor
- `eview` — wraps `less` with `ecolor` as preprocessor; used by `esearch` for full-file viewing
- `esearch` — interactive full-content search via `rg` + `fzf` with `ecolor` preview
- `elocate` — locate files by name via `fzf` with `ecolor` preview
- `R Markdown.sublime-syntax` — bat syntax definition; copy to `~/.config/bat/syntaxes/` and run `bat cache --build`

## Running and testing

There is no build step. Scripts run directly as bash:

```bash
./etext test/pdf/somefile.pdf          # convert to Markdown, print to stdout
./etext test/pdf/somefile.pdf --filename  # write to cache, print cache path
./etext                                # prune cache and show count
./ecolor test/images/photo.jpg         # colorized output for less
./eview test/documents/report.docx     # open in less with ecolor
./esearch keyword                      # interactive search
./elocate filename                     # interactive locate
```

Test files live in `test/` organized by type: `audio/`, `compressed/`, `documents/`, `ebooks/`, `html/`, `images/`, `ipynb/`, `misc/`, `pdf/`, `presentations/`, `svg/`, `tabular/`.

To see log output: `journalctl -t ecolor -t etext`. Set `ETEXT_DEBUG=1` to enable `etext` logging.

## Architecture

### `etext` dispatch and caching

`etext` dispatches to handler functions based on file extension (case-insensitive). The handler chain for complex formats chains tools: `LibreOffice → pptx2md → cache`, `Calibre → Pandoc → cache`, etc. The cache lives at `${XDG_CACHE_HOME:-$HOME/.cache}/everything/` using a 128-bit BLAKE2 hash of the absolute path as the filename (`*.md`). A `.tmp` suffix marks in-progress writes; on success the `.tmp` is `mv`-ed to the final name. Cache entries older than 30 days are pruned when `etext` is called with no arguments.

### Two output modes of `etext`

- Without `--filename`: prints the text content to stdout (used by `rg --pre etext`)
- With `--filename`: writes to cache and prints the cache path (used by `ecolor`)

### Environment variables that cross process boundaries

- `ESEARCH_PATTERN` / `ESEARCH_OPTIONS` — set by `esearch`, read by `ecolor` to highlight matching lines in preview
- `ETEXT_ERR` — path to a temp file where `etext` accumulates non-fatal errors; `esearch` displays them after `fzf` exits
- `ETEXT_DEBUG` — enables `logger`-based debug logging in `etext`
- `LESSOPEN` / `LESSCLOSE` / `COLUMNS` — set by `eview` to wire `ecolor` as the preprocessor
- `EZA_OPTIONS` — set by the user in their shell profile; read by `ecolor` when listing directories with `eza`

### External tool dependencies

Pandoc, `pdftohtml` (poppler-utils), `pptx2md`, Calibre's `ebook-convert`, LibreOffice, ExifTool (`exiftool`), `xsltproc`, `bat`/`batcat`, `eza`, `hexyl`, `chafa`, `rg`, `fzf`, `locate`, `b2sum`, `file`, `stat`.

`bat` is found at runtime via `type -P bat batcat | head -n1` to handle both names.

### `mcp-server/` subdirectory

A Python MCP server (`mcp-server/everything_mcp.py`) that exposes `etext` and `rg --pre etext` to Claude Desktop / Cowork. Three tools:

- `list_dir(path)` — one-level directory listing via `os.scandir`
- `search(pattern, path, ...)` — `rg --pre etext --json` with optional `ignore_case`, `glob`, `max_count`, `context`/`before`/`after` (-C/-B/-A)
- `fetch(file, [start, end])` — `etext <file>` stdout mode, optionally sliced to a line range

The server is installed as an executable (`everything-mcp`) via `uv` or `pipx`:

```bash
uv tool install 'git+https://github.com/allefeld/everything.git#subdirectory=mcp-server'
# or from local checkout:
cd mcp-server && uv tool install --force --reinstall .
```

`etext` is resolved via `shutil.which("etext")` at runtime — it must be on `$PATH`, not at a hardcoded path. After editing `everything_mcp.py`, reinstall with the local-checkout command above before testing. The `pyproject.toml` uses `setuptools.build_meta` with `py-modules = ["everything_mcp"]`.

### `ecolor` file-type routing

1. Non-existing / broken symlink → red message
2. Directory → `eza` listing
3. Special file (pipe/socket/block/char device) → `stat` output highlighted with `bat --language meminfo`
4. Empty file → red message
5. Regular file → `etext "$pn" --filename`, then if encoding is binary: `file` + `hexyl`; if text: `bat` (with `rg`-based line highlights when `ESEARCH_PATTERN` is set), followed by a `chafa` terminal-graphics rendering of the original file (silently no-ops on non-image input)
