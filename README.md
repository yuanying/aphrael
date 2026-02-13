# aphrael

A standalone Python package that extracts [calibre](https://calibre-ebook.com/)'s ebook conversion engine, focused on EPUB / MOBI / AZW3 formats.
Unnecessary modules (GUI, device integration, etc.) have been removed and C extensions replaced with pure Python, resulting in a lightweight CLI-only converter.

[日本語](README.ja.md)

## Supported Formats

| Direction | Formats |
|-----------|---------|
| Input     | EPUB, MOBI, AZW3, AZW, PRC, KEPUB |
| Output    | EPUB, MOBI, AZW3, OEB |

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended)

## Installation

The easiest way is to install via `uv tool install`:

```bash
uv tool install git+https://github.com/yuanying/aphrael.git
```

After installation, the `aphrael` command is available directly:

```bash
aphrael --version
```

## Usage

Basic syntax:

```bash
aphrael <input_file> <output_file> [options]
```

The output format is automatically determined from the file extension of the output file.

### Examples

```bash
# EPUB to MOBI
aphrael book.epub book.mobi

# EPUB to AZW3
aphrael book.epub book.azw3

# AZW3 to EPUB
aphrael book.azw3 book.epub

# Derive output filename from input, specifying only the extension
aphrael book.epub .mobi
```

### Checking Available Options

Available options vary depending on the input and output formats. To see format-specific options:

```bash
aphrael input.epub output.mobi -h
```

For detailed documentation on the conversion system, refer to the calibre manual:
https://manual.calibre-ebook.com/conversion.html

## Development

```bash
git clone https://github.com/yuanying/aphrael.git
cd aphrael
uv sync
```

### Testing

```bash
uv run pytest tests/
```

### Linting

```bash
uv run ruff check src/
```

## License

GPL-3.0-only (same as calibre)
