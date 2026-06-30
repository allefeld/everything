# Search and view Everything

Everything provides a suite of tools to make the content of files of as many types as possible textually searchable and viewable in the terminal. It was inspired by [ripgrep-all](https://github.com/phiresky/ripgrep-all), but goes beyond its functionality.

## Tools

- **`etext`** — converts binary and rich-text files to Markdown for text processing. Used as a preprocessor for `ripgrep` (via `rg --pre etext`) to enable full-text search across PDFs, Office documents, ebooks, archives, images, and more. Dispatches to external converters (Pandoc, LibreOffice, Calibre) based on file extension and caches results for performance.

- **`ecolor`** — renders files as colored text for viewing in `less`. Wraps `etext` for binary files and adds syntax highlighting via `bat`. Shows directory listings, hexdumps for binary files, and terminal-graphics renderings of images. Used as the `LESSOPEN` preprocessor by `eview`.

- **`eview`** — interactive file viewer. Wraps `less` with `ecolor` as preprocessor to display any file type with automatic conversion and highlighting. Supports `less` navigation (Ctrl+Left/Right to switch between multiple open files).

- **`esearch`** — interactive full-content search. Uses `ripgrep` (via `etext --pre`) to search across all file types, and `fzf` for an interactive interface with live `ecolor` preview of matching files. Displays `etext` conversion errors after exiting.

- **`elocate`** — locate files by name. Uses the system `locate` database with `fzf` for interactive filtering and `eview` for full-file preview. Filters to files under the current directory and excludes hidden files.

- **`R Markdown.sublime-syntax`** — extended `bat` syntax definition for R Markdown and Quarto files. Enables syntax highlighting of YAML front-matter and mixed Markdown/R/Python content in `.md`, `.qmd`, and `.Rmd` files.

Everything is developed on Debian GNU/Linux (trixie), but should work on other modern Linux distributions.

## Installation

Copy the script files into a directory on your `$PATH`, e.g. `$HOME/.local/bin/`:

```bash
chmod +x etext ecolor eview esearch elocate
cp etext ecolor eview esearch elocate ~/.local/bin/
```

Copy `R Markdown.sublime-syntax` into `bat`'s syntax directory and rebuild its cache:

```bash
mkdir -p ~/.config/bat/syntaxes
cp "R Markdown.sublime-syntax" ~/.config/bat/syntaxes/
bat cache --build
```

Note: `bat` may be installed as `batcat` on Debian. If so, either use `alias bat=/usr/bin/batcat` in your shell or update the scripts to use the correct command name.

## Requirements

The following tools are required:

**Core tools:** `bash`, `grep`, `sed`, `file`, `stat`, `mktemp`

**Paging & interaction:** `less`, `fzf`, `bat` (or `batcat`), `eza`

**Search & locate:** `rg` (ripgrep), `locate` (from `mlocate` or `plocate`)

**File format conversions:** Pandoc, LibreOffice, Calibre's `ebook-convert`, `pptx2md`, `xsltproc` (libxslt), ExifTool (`exiftool`), `pdftohtml` (poppler-utils)

**Binary file display:** `hexyl`, `chafa`

**Compression tools:** `gunzip`, `bunzip2`, `unzip`, `unzstd` (from `zstd`), support for `.xz` and `.lz4`

**Hashing:** `b2sum` (from `coreutils`)

### On Debian/Ubuntu

Install the packages:

```bash
apt-get install bash bat bzip2 calibre coreutils exiftool file fzf gzip hexyl less libreoffice-common libxslt1.1 mlocate pandoc poppler-utils ripgrep sed unzip xsltproc zstd chafa exiftool
```

Additionally, install `pptx2md` from source or pip (not in official Debian packages yet):

```bash
pip install pptx2md
```

### Optional: Newer versions

If your distribution's packages are out of date, install newer versions from upstream:

- [bat](https://github.com/sharkdp/bat)
- [Calibre](https://calibre-ebook.com/)
- [chafa](https://hpjansson.org/chafa/)
- [fzf](https://github.com/junegunn/fzf)
- [hexyl](https://github.com/sharkdp/hexyl)
- [Pandoc](https://github.com/jgm/pandoc)
- [ripgrep](https://github.com/BurntSushi/ripgrep)
- [pptx2md](https://github.com/ssine/pptx2md)

### Performance

During conversion, `etext` creates temporary files and directories using `mktemp`. For best performance, ensure `/tmp` (or the directory specified by `$TMPDIR`) is memory-backed (tmpfs/ramfs).

## Usage

```bash
etext <file>                        # Convert file to Markdown, print to stdout
etext <file> --filename             # Convert file to Markdown, write to cache, print cache path
etext                               # Prune cache entries older than 30 days, show count
ecolor <file>                       # Display file with colors (used by eview/esearch)
eview [files...]                    # Open file(s) in less with etext conversion and highlighting
esearch <pattern>                   # Interactive full-content search across all file types
elocate <name>                      # Locate files by name with interactive selection
```

## Logging

By default, `ecolor` always logs to the system log (via `logger`), and `etext` is silent unless `ETEXT_DEBUG=1` is set. View log messages with:

```bash
journalctl -t ecolor -t etext
```
