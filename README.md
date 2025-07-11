# Email Polling System

## 概要

メールポーリングシステムは、定期的にGmailをポーリングして新しいメールを取得し、PDF添付ファイルを処理してNotionデータベースに登録するシステムです。

## 機能

1. **メールポーリング**: 定期的にGmailから未読メールを取得
2. **ファイル保存**: メールファイル(.eml)とPDF添付ファイルをローカルに保存
3. **X-API連携**: PDFファイルをX-APIにアップロード（モック実装）
4. **Dify OCR処理**: PDFファイルのOCR処理（モック実装）
5. **Notion連携**: 処理結果をNotionデータベースに登録

## 開発環境

### 必要な環境

- Python 3.8+
- Gmail アカウント（アプリパスワード設定済み）
- Notion アカウント（Integration Token取得済み）

### セットアップ

```bash
# プロジェクトディレクトリに移動
cd backend/

# 依存関係のインストール
pip install -r requirements.txt

# 環境変数の設定
cp .env.example .env
# .envファイルを編集して必要な設定を入力

# アプリケーションの起動
python -m app.main
```

### API ドキュメント

アプリケーション起動後、以下のURLでSwagger UIにアクセスできます：

http://localhost:8000/api/docs

## API エンドポイント

### メール関連

- `GET /api/v1/emails/status` - メールポーリングの状態を取得
- `POST /api/v1/emails/poll` - 手動でメールポーリングを実行
- `GET /api/v1/emails/latest` - 最新のメール一覧を取得

## 設定

### Gmail設定

1. Googleアカウントで2段階認証を有効化
2. アプリパスワードを生成
3. `.env`ファイルに設定

```env
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
```

### Notion設定

1. Notion Integrationを作成
2. データベースにIntegrationを招待
3. `.env`ファイルに設定

```env
NOTION_TOKEN=your-notion-integration-token
NOTION_DATABASE_ID=your-notion-database-id
```

## ファイル構造

```
backend/
├── app/
│   ├── main.py                 # FastAPIアプリケーション
│   ├── core/
│   │   └── settings.py         # 設定管理
│   ├── api/
│   │   └── v1/
│   │       └── emails/         # メール関連API
│   ├── services/
│   │   ├── email_service.py    # メール処理サービス
│   │   ├── x_api_service.py    # X-API連携（モック）
│   │   ├── dify_service.py     # Dify OCR連携（モック）
│   │   └── notion_service.py   # Notion API連携
│   └── scheduler/
│       ├── main.py             # スケジューラー管理
│       └── jobs/
│           └── email_polling_job.py  # メールポーリングジョブ
├── .env.example                # 環境変数テンプレート
└── requirements.txt            # 依存関係
```

## 今後の拡張予定

- [ ] SMTP対応
- [ ] X-API実装
- [ ] Dify OCR実装
- [ ] エラーハンドリング強化
- [ ] ログ機能追加
- [ ] データベース連携
