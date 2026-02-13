# aphrael

[calibre](https://calibre-ebook.com/) の電子書籍変換エンジンを EPUB / MOBI / AZW3 に特化して抽出したスタンドアロン Python パッケージです。
GUI やデバイス連携などの不要モジュールを除去し、C 拡張を純粋 Python で置き換えることで、軽量かつ CLI だけで変換が完結します。

[English](README.md)

## 対応フォーマット

| 方向 | フォーマット |
|------|-------------|
| 入力 | EPUB, MOBI, AZW3, AZW, PRC, KEPUB |
| 出力 | EPUB, MOBI, AZW3, OEB |

## 要件

- Python 3.10 以上
- [uv](https://docs.astral.sh/uv/) (推奨)

## インストール

`uv tool install` を使ってシステムワイドにコマンドを導入するのが最も簡単です。

```bash
uv tool install git+https://github.com/yuanying/aphrael.git
```

インストール後は `aphrael` コマンドがそのまま使えます。

```bash
aphrael --version
```

## 使い方

基本構文:

```bash
aphrael <入力ファイル> [出力ファイル] [オプション]
```

出力ファイルを省略した場合、入力ファイルと同じディレクトリに AZW3 (KF8) 形式の `.mobi` ファイルがデフォルト生成されます。Kindle Paperwhite は `.mobi` ファイルの内部フォーマットを自動判別するため、追加の引数なしで Kindle 向けの最適な出力が得られます。

出力ファイルを指定した場合は、その拡張子から出力フォーマットが自動判定されます。

### 変換例

```bash
# デフォルト出力: book.mobi (AZW3/KF8 形式) を Kindle 向けに生成
aphrael book.epub

# EPUB → MOBI
aphrael book.epub book.mobi

# EPUB → AZW3
aphrael book.epub book.azw3

# AZW3 → EPUB
aphrael book.azw3 book.epub

# 入力ファイル名をそのまま使い、拡張子だけ指定
aphrael book.epub .mobi
```

### オプションの確認

入力・出力フォーマットによって利用可能なオプションが変わります。具体的なオプションを確認するには:

```bash
aphrael input.epub output.mobi -h
```

変換システムの詳細なドキュメントは calibre のマニュアルを参照してください:
https://manual.calibre-ebook.com/conversion.html

## 開発

```bash
git clone https://github.com/yuanying/aphrael.git
cd aphrael
uv sync
```

### テスト

```bash
uv run pytest tests/
```

### リント

```bash
uv run ruff check src/
```

## ライセンス

GPL-3.0-only (calibre と同一)
