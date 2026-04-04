# Search and view Everything

Everything provides a number of tools to make the content of files of as many types as possible textually searchable and viewable in the terminal. It was inspired by [ripgrep-all](https://github.com/phiresky/ripgrep-all), but goes beyond its functionality.

-   `etext` is designed as a preprocessor for the fast recursive search tool `ripgrep`. It tries to represent the content of different types of binary files (as well as some hard-to-read markup formats like HTML) as Markdown. `etext` uses external conversion tools such as Pandoc, `ebook-convert` (packaged with Calibre) and LibreOffice. To dispatch to different converters quickly, it uses the file extension only. 

-   `ecolor` is designed as a preprocessor for the standard pager `less`. It uses `etext` to obtain a Markdown representation for binary files, but also processes file types not covered by `etext`, and adds syntax highlighting provided by `bat`, relying on its type detection based on file extension and file content. For non-converted binary files `ecolor` shows a type description from `file` and a hexdump from `hexyl`. In addition to regular files, it can show directory listings and basic information about special files.

- `R Markdown.sublime-syntax` is a version of the file available from <https://github.com/randy3k/R-Box/>, slightly patched to additionally apply to the file extensions `md` and `qmd`. Among other things, this enables `bat` to syntax-highlight a YAML metadata block at the beginning of a Markdown file as used by Pandoc (as well as R Markdown and Quarto).

Everything is developed on Debian GNU/Linux (trixie), but should work on other modern Linux distributions, too.


## Installation

Copy `etext` and `ecolor` into a directory on the path, e.g. `$HOME/.local/bin/`.

In your `.bashrc` or other initialization file, execute `eval $(ecolor)` to set and export `LESSOPEN`, `LESSCLOSE`, and `LESS`, and to export `COLUMNS`.

Copy `R Markdown.sublime-syntax` into `bat`'s syntax directory (standard `$HOME/.config/bat/syntaxes/`) and run `bat cache --build`. If `bat` was installed under the name `batcat` (Debian-packaged), use that name instead (or define `alias bat="/usr/bin/batcat"`).


## Requirements

The following tools are assumed to be installed: `bash`, `bat` (`batcat)`, `bunzip2`, `ebook-convert`, `file`, `fzf`, `grep`, `gunzip`, `hexyl`, `less`, `libreoffice`, `lsd`, `pandoc`, `rg`, `sed`, `unzip`, `unzstd`, `yq`.

On Debian, they are contained in the packages `bash bat bzip2 calibre file fzf grep gzip hexyl less libreoffice-common lsd pandoc ripgrep sed unzip zstd yq`.

Occasionally, a Debian-packaged version may not be sufficiently up to date. In that case, install a newer version from [bat](https://github.com/sharkdp/bat), [Calibre](https://calibre-ebook.com/), [fzf](https://github.com/junegunn/fzf), [hexyl](https://github.com/sharkdp/hexyl), [lsd](https://github.com/lsd-rs/lsd), [Pandoc](https://github.com/jgm/pandoc), [ripgrep](https://github.com/BurntSushi/ripgrep), [yq](https://github.com/mikefarah/yq).

During conversion, `etext` creates temporary files and directories using `mktemp`. To keep the process fast, `/tmp` (or `TMPDIR` if set) should be memory-backed.


## Logging

`ecolor` always logs to the system log, `etext` only if `ETEXT_DEBUG` is set. To see log messages from both, use `journalctl -t ecolor -t etext`.


TODO: update README
