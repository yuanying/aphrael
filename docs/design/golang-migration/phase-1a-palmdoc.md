# Phase 1-A: PalmDoc 圧縮

## 概要

Go 移植の最初のモジュールとして PalmDoc LZ77 圧縮/展開を移植する。純アルゴリズムで外部依存がなく、移植パイプラインの検証に最適。

**対象ソース**: `src/calibre/ebooks/compression/palmdoc.py` (102行)

---

## Python API（移植対象）

### `decompress_doc(data: bytes) -> bytes`

- 空バイト列 → 空バイト列
- PalmDoc LZ77 圧縮データを展開
- 4種のバイトパターンを処理:
  1. `c=1-8`: 次の c バイトをリテラルコピー
  2. `c=9-0x7f`: リテラル1バイト出力
  3. `c>=0xc0`: スペース + (c XOR 0x80) の2バイト出力
  4. `c=0x80-0xbf`: LZ77 後方参照（距離最大2047、長さ3-10）

### `compress_doc(data: bytes) -> bytes`

- 空バイト列 → 空バイト列
- `py_compress_doc` を呼ぶ（同一関数）
- 3種のエンコード:
  1. **LZ77**: 過去データから3-10バイト一致を検索、距離最大2047
  2. **スペース+文字**: ` `+0x40-0x7f → 1バイト (c XOR 0x80)
  3. **バイナリシーケンス**: 0x01-0x08のプレフィックス+最大8バイト
  4. **リテラル**: それ以外は1バイトそのまま

---

## Go パッケージ

**パス**: `internal/compression/palmdoc/`

### API 設計

```go
package palmdoc

// Decompress は PalmDoc LZ77 圧縮データを展開する
func Decompress(data []byte) ([]byte, error)

// Compress は PalmDoc LZ77 形式でデータを圧縮する
func Compress(data []byte) []byte
```

---

## 実行ステップ

### ステップ 1: Python テスト追加

**ファイル**: `tests/unit/test_palmdoc.py`

既存テスト:
- `test_compress_decompress_roundtrip`: 5パターンのラウンドトリップ
- `test_compress_empty` / `test_decompress_empty`: 空データ
- `test_py_compress_matches`: compress_doc == py_compress_doc

追加するテスト:
1. **ゴールデンテスト (compress)**: 既知入力 → 圧縮結果をバイナリで固定
   - `b"Hello, World!"` → compress → 期待バイト列を assert
   - ラウンドトリップだけでなく中間出力も検証
2. **ゴールデンテスト (decompress)**: 既知の圧縮データ → 展開結果を固定
3. **LZ77 エッジケース**:
   - 全く同じ文字列の繰り返し (`b"abcabc" * 100`)
   - 距離=1 の繰り返し (`b"aaaa..."`)
   - 距離=2047 付近のマッチ
4. **バイナリシーケンス**: 制御文字 0x01-0x08 の入力
5. **スペース+文字エンコード**: `b" A"`, `b" z"`, `b" @"` (0x40-0x7f範囲)
6. **大きなデータ**: 4096バイト以上のデータ
7. **フィクスチャ生成**: テストデータを `testdata/golden/palmdoc/` に書き出す関数

### ステップ 2: フィクスチャ生成スクリプト

**ファイル**: `tests/golden_gen/gen_palmdoc.py`

- 上記テストケースの入力と compress/decompress 出力を `testdata/golden/palmdoc/` に保存
- ファイル命名: `<case_name>_input.bin`, `<case_name>_compressed.bin`

### ステップ 3: Go テスト

**ファイル**: `internal/compression/palmdoc/palmdoc_test.go`

- `testdata/golden/palmdoc/` から fixture を読み込む
- `TestDecompress`: 各ゴールデン compressed → 元データに一致
- `TestCompress`: 各ゴールデン input → compressed に一致
- `TestRoundtrip`: compress → decompress が元に戻る
- `TestEmpty`: 空入力
- `TestEdgeCases`: エッジケース群

### ステップ 4: Go 実装

**ファイル**: `internal/compression/palmdoc/palmdoc.go`

- `decompress_doc` の Python ロジックを Go に直訳
- `py_compress_doc` の Python ロジックを Go に直訳
- 使用する標準ライブラリ: `bytes`, `encoding/binary`

---

## 完了条件

- [ ] `uv run pytest tests/unit/test_palmdoc.py` 全テスト通過
- [ ] `go test ./internal/compression/palmdoc/` 全テスト通過
- [ ] Python と Go の compress 出力が全ケースで完全一致
- [ ] Python と Go の decompress 出力が全ケースで完全一致
