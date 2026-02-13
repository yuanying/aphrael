# aphrael CLAUDE.md

## 必須チェック項目

毎ステップで以下を確認すること:

1. `uv run ruff check src/` でリントエラーがないことを確認
2. `uv run pytest tests/` でテストが通ることを確認
3. コミット前に上記両方を実行すること

## プロジェクト概要

calibre の `ebook-convert` ツールを基に EPUB/MOBI/AZW3 のみ対応のスタンドアロン Python パッケージとして再構成。
C 拡張を純粋 Python で置き換え、不要モジュール（GUI, AI, デバイス等）を除去。
