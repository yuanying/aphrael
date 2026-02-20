# aphrael Go 移植計画

## Context

aphrael は calibre の `ebook-convert` を基にした EPUB/MOBI/AZW3 対応の電子書籍変換ツール（Python、約72,000行、228ファイル）。これを Go に移植する。

**移行方針**: TDD ボトムアップ。各モジュールについて以下の3ステップで進める:
1. Python で単体テストを追加し、既存の挙動（外部ライブラリの挙動含む）を把握
2. Go で同等の単体テストを作成（最初は全て失敗）
3. Go でテストをパスさせる実装を書く

---

## ベースライン品質（2026-02-14 時点）

- `uv run ruff check src/` → **All checks passed**
- `uv run pytest tests/` → **44 passed, 3 skipped**
- 実コード規模（Python）:
  - `src/calibre`: **65,092行**
  - `src/calibre/ebooks/oeb`: **16,537行**
  - `src/calibre/utils`: **14,777行**
  - `src/calibre/ebooks/mobi`: **11,088行**
  - `src/calibre/ebooks/metadata`: **6,614行**
  - `src/calibre/ebooks/conversion`: **5,195行**

---

## プロジェクト構造（Python/Go 混在・同一リポジトリ）

```
aphrael/                         # github.com/yuanying/aphrael
├── src/                         # Python ソース（既存）
│   ├── calibre/
│   ├── polyglot/
│   ├── css_selectors/
│   └── tinycss/
├── tests/                       # Python テスト（既存）
├── cmd/aphrael/main.go          # Go CLI エントリポイント
├── internal/                    # Go 内部パッケージ
│   ├── compression/palmdoc/     # PalmDoc LZ77
│   ├── encoding/chardet/        # エンコーディング検出
│   ├── textutil/                # cleantext, icu, smartypants
│   ├── xmlutil/                 # XML/HTMLパース (lxml代替ラッパー)
│   ├── imgutil/                 # 画像処理
│   ├── css/
│   │   ├── tokenizer/          # tinycss トークナイザ
│   │   ├── parser/             # CSS2.1 + CSS3パーサ
│   │   ├── selector/           # CSSセレクタ (cascadia拡張)
│   │   ├── normalize/          # CSS正規化
│   │   └── stylizer/           # CSSスタイル計算
│   ├── oeb/                    # OEB中間表現
│   ├── metadata/               # OPF2/3メタデータ
│   ├── mobi/                   # MOBI/KF8 reader/writer
│   ├── epub/                   # EPUB reader/writer/container
│   ├── conversion/             # 変換パイプライン
│   └── fileutil/               # ファイル名, ZIP, 一時ディレクトリ
├── pkg/aphrael/                 # Go 公開API
├── testdata/                    # ゴールデンテストデータ（Python/Go共有）
├── pyproject.toml               # Python プロジェクト設定（既存）
├── go.mod                       # go mod init github.com/yuanying/aphrael
└── go.sum
```

---

## ライブラリ戦略

| Python ライブラリ | Go 代替 | 戦略 |
|---|---|---|
| lxml (39ファイル) | `beevik/etree` + `antchfx/xpath,xmlquery,htmlquery` + `x/net/html` | ラッパー層構築 |
| css-parser (18ファイル) | **再実装** | tinycss Go版の上に必要機能のみ構築 |
| tinycss (同梱, 2,842行) | **再実装** | `gorilla/css/scanner` を参考に |
| css_selectors (同梱, 2,494行) | `andybalholm/cascadia` 拡張 | XHTML名前空間対応を追加 |
| Pillow (6ファイル) | `image/*` 標準 + `x/image/draw` | 使用機能が限定的 |
| chardet | `x/text/encoding` + `saintfish/chardet` | 標準+サードパーティ |
| html5-parser/html5lib/bs4 | `x/net/html` | 標準拡張で十分 |
| regex | `regexp` + `dlclark/regexp2` | 必要に応じて |

**再実装が必須なモジュール**: tinycss, css-parser使用部分, stylizer, normalize_css

---

## ボトムアップ移植順（確定版）

1. `src/calibre/ebooks/compression/palmdoc.py`
2. `src/calibre/ebooks/chardet.py`
3. `src/calibre/utils/cleantext.py`, `src/calibre/utils/icu.py`
4. `src/calibre/utils/zipfile.py`, `src/calibre/utils/localunzip.py`, `src/calibre/utils/filenames.py`
5. `src/calibre/ebooks/oeb/parse_utils.py`, `src/calibre/ebooks/oeb/base.py`
6. `src/calibre/ebooks/oeb/polish/parsing.py`, `src/calibre/ebooks/oeb/polish/container.py`
7. `src/calibre/ebooks/metadata/opf2.py`, `src/calibre/ebooks/metadata/opf3.py`, `src/calibre/ebooks/metadata/epub.py`
8. `src/calibre/ebooks/mobi/*`（reader/writer）
9. `src/calibre/ebooks/conversion/plumber.py`, `src/calibre/ebooks/conversion/cli.py`

---

## フェーズ詳細

### [Phase 0: プロジェクト基盤](phase-0-foundation.md)

- Go プロジェクト初期化 (`go mod init`)
- Python側にゴールデンテスト出力生成の仕組みを構築
- テストデータ（サンプル EPUB/MOBI）の準備

### Phase 1: Foundation Layer（依存なしモジュール）

#### [1-A: PalmDoc 圧縮](phase-1a-palmdoc.md)

- **対象**: `src/calibre/ebooks/compression/palmdoc.py` (102行)
- **難易度**: 低

#### 1-B: cleantext

- **対象**: `src/calibre/utils/cleantext.py` (90行)
- **難易度**: 低

#### 1-C: ICU互換

- **対象**: `src/calibre/utils/icu.py` (251行)
- **難易度**: 低〜中

#### 1-D: XML名前空間ユーティリティ

- **対象**: `src/calibre/ebooks/oeb/parse_utils.py` の `barename`, `namespace` 関数
- **難易度**: 低

### Phase 2: Low-Level Utilities

#### 2-A: エンコーディング検出

- **対象**: `src/calibre/ebooks/chardet.py` (191行)
- **難易度**: 中

#### 2-B: ZIP/ファイルI/O基盤

- **対象**: `src/calibre/utils/zipfile.py`, `src/calibre/utils/localunzip.py`, `src/calibre/utils/filenames.py`
- **難易度**: 中

#### 2-C: XMLパース（最重要ユーティリティ）

- **対象**: `src/calibre/utils/xml_parse.py` (139行)
- **難易度**: 高（プロジェクト全体のXML/HTML処理基盤）

#### 2-D: 画像処理

- **対象**: `src/calibre/utils/img.py` (234行)
- **難易度**: 中

#### 2-E: その他ユーティリティ

- `utils/logging.py` → Go `log/slog`
- `utils/filenames.py` → Go `path/filepath` + `os`
- `utils/date.py` → Go `time`
- `utils/imghdr.py` → マジックバイト判定

### Phase 3: CSS処理（最大の技術的挑戦）

#### 3-A: tinycss トークナイザ/パーサ再実装

- **対象**: `src/tinycss/` (2,842行)
- **難易度**: 高

#### 3-B: CSSセレクタ

- **対象**: `src/css_selectors/` (2,494行)
- **難易度**: 中〜高

#### 3-C: css-parser依存処理

- **対象**: 18ファイルで使用されている css-parser の機能
- **難易度**: 高

#### 3-D: CSS正規化

- **対象**: `src/calibre/ebooks/oeb/normalize_css.py`
- **難易度**: 中

### Phase 4: OEB 中間表現

#### 4-A: OEB base

- **対象**: `src/calibre/ebooks/oeb/base.py` (2,025行)
- **難易度**: 高

#### 4-B: Metadata

- **対象**: `metadata/opf2.py` (1,904行), `metadata/opf3.py` (1,188行)
- **難易度**: 中〜高

#### 4-C: Polish コンテナ

- **対象**: `src/calibre/ebooks/oeb/polish/parsing.py`, `src/calibre/ebooks/oeb/polish/container.py`
- **難易度**: 高

### Phase 5: MOBI/KF8 処理

#### 5-A: MOBI 共通ユーティリティ

- **対象**: `mobi/langcodes.py`, `mobi/utils.py`, `mobi/huffcdic.py`
- **難易度**: 低〜中

#### 5-B: MOBI Reader

- **対象**: `mobi/reader/` (headers.py, index.py, markup.py, mobi6.py, mobi8.py)
- **難易度**: 中

#### 5-C: MOBI Writer

- **対象**: `mobi/writer2/` (MOBI6), `mobi/writer8/` (KF8)
- **難易度**: 中〜高

### Phase 6: EPUB 処理

#### 6-A: EPUB コンテナ

- **対象**: `epub/__init__.py`
- **難易度**: 低

#### 6-B: EPUB Input/Output

- **対象**: `conversion/plugins/epub_input.py`, `epub_output.py`
- **難易度**: 中

### Phase 7: Transforms と Stylizer

#### 7-A: Stylizer

- **対象**: `oeb/stylizer.py` (889行)
- **難易度**: 高

#### 7-B: Transforms

- `flatcss.py` (706行) → `split.py` → `structure.py` → `cover.py`

#### 7-C: Polish

- `container.py` (1,640行), `toc.py` (918行), `cascade.py`, `kepubify.py`

### Phase 8: Conversion Pipeline

#### 8-A: Plumber

- **対象**: `conversion/plumber.py` (1,301行)

#### 8-B: CLI

- Go `cobra` or `flag` でCLI実装

#### 8-C: エンドツーエンド検証

- Python版とGo版で同一入力を変換し出力比較

---

## 検証戦略

1. **ゴールデンテスト**: Python 側で `testdata/golden/` にゴールデン出力を生成 → Go で同じ出力と比較
2. **ラウンドトリップ**: 変換→逆変換の一貫性
3. **ファズテスト**: Go `testing.F` で PalmDoc, CSS tokenizer, HTML/XML parser, MOBI header
4. **E2E比較**: サンプル EPUB/MOBI を両バージョンで変換し diff
5. **同型テスト原則**:
   - 先に Python に characterization test を追加
   - 期待値（JSON/バイナリ）を fixture 化
   - Go で同一 fixture を読む単体テストを実装
   - 差分ゼロを確認してから次モジュールへ進む
