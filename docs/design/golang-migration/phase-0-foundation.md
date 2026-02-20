# Phase 0: プロジェクト基盤

## 概要

Go 移植の土台となるプロジェクト基盤を構築する。Go モジュールの初期化、開発規約の策定、ゴールデンテスト基盤の準備を行う。

---

## 作業項目

### 1. Go プロジェクト初期化

- `go mod init github.com/yuanying/aphrael`
- Go バージョン: 1.23+
- `.gitignore` に Go ビルド成果物を追加

### 2. Go 開発規約

- **lint**: `golangci-lint`（設定ファイル `.golangci.yml` を作成）
- **テスト実行**: `go test ./internal/...`
- **ディレクトリ規約**:
  - `internal/` — 非公開パッケージ
  - `pkg/` — 公開 API
  - `cmd/` — CLI エントリポイント

### 3. ゴールデンテスト基盤

Python と Go で同一のテストデータを共有する仕組みを構築する。

- **fixture 保存先**: `testdata/golden/<module>/`
- **Python 側**: `tests/golden_gen/` にフィクスチャ生成スクリプトを配置
- **フォーマット**: バイナリデータは `.bin`、構造化データは `.json`
- **フロー**: Python → `testdata/golden/` に出力 → Go テストで同一ファイルを読む

---

## 完了条件

- [ ] `go mod init` 完了、`go.mod` が存在する
- [ ] `.golangci.yml` が存在する
- [ ] `testdata/golden/` ディレクトリが存在する
- [ ] `.gitignore` に Go 関連エントリが追加されている
