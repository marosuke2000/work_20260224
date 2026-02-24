# ポモドーロタイマー

FlaskとHTML/CSS/JavaScriptを用いたポモドーロタイマーWebアプリケーション。

## 機能

- 25分の作業タイマー
- 開始・リセットボタン
- 残り時間の表示
- 円グラフによる進捗表示
- 今日の進捗（完了回数、集中時間）の表示

## 技術スタック

- **Backend**: Python 3.11+ / Flask 3.0
- **Frontend**: HTML5 / CSS3 / JavaScript
- **Testing**: pytest 7.4

## ディレクトリ構成

```
1.pomodoro/
├── app.py              # Flaskアプリ本体
├── timer.py            # タイマーロジック（ビジネスロジック）
├── templates/
│   └── index.html      # メイン画面
├── static/
│   ├── css/
│   │   └── style.css   # スタイルシート
│   └── js/
│       └── timer.js    # タイマー管理・UI操作
├── tests/
│   ├── __init__.py
│   ├── test_timer.py   # タイマーロジックのテスト
│   └── test_app.py     # Flaskアプリのテスト
├── requirements.txt    # Python依存関係
├── architecture.md     # アーキテクチャ設計書
├── features.md         # 機能一覧
└── plan.md            # 実装計画
```

## セットアップ

### 依存関係のインストール

```bash
cd 1.pomodoro
pip install -r requirements.txt
```

## 実行方法

### アプリケーションの起動

```bash
python app.py
```

ブラウザで http://localhost:5000 にアクセスしてください。

## テスト

### テストの実行

```bash
# 全テストを実行
python -m pytest tests/ -v

# カバレッジ付きでテストを実行
python -m pytest tests/ --cov=. --cov-report=term-missing

# 特定のテストファイルのみ実行
python -m pytest tests/test_timer.py -v
```

### テスト結果

現在、26個のユニットテストが実装されており、すべて成功しています：

- **test_timer.py**: タイマーロジックのテスト（17テスト）
  - 初期化、開始、tick処理、状態遷移、リセット、進捗率計算など
- **test_app.py**: Flaskアプリのテスト（9テスト）
  - ルート確認、HTML要素の検証、静的ファイルの読み込みなど

**テストカバレッジ**: 98%

## 開発

### アーキテクチャ

詳細は [architecture.md](architecture.md) を参照してください。

主な設計方針：
- タイマーロジックをPythonクラス（timer.py）として分離し、ユニットテストしやすい設計
- フロントエンドとバックエンドの責務を明確に分離
- DIやモックを活用したテスト設計

### 実装計画

実装は段階的に進めています。詳細は [plan.md](plan.md) を参照してください。

- ✅ 第1段階: 最小機能タイマーの実装（完了）
- 🚧 第2段階: 進捗管理・UI拡張
- 📋 第3段階: 休憩タイマー・状態切替
- 📋 第4段階: 通知・アラート機能
- 📋 第5段階: データ保存・API連携
- 📋 第6段階: テスト・保守性向上
- 📋 第7段階: 拡張・最適化

## ライセンス

MIT License
