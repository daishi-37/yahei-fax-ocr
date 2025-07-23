# Gmailポーリングテストガイド

このガイドでは、Gmailポーリング機能のテスト方法について説明します。

## 事前準備

### 1. Gmailアプリパスワードの設定

Gmailの2段階認証を有効にして、アプリパスワードを生成する必要があります。

1. [Googleアカウント設定](https://myaccount.google.com/)にアクセス
2. 「セキュリティ」→「2段階認証プロセス」を有効化
3. 「アプリパスワード」を生成
4. 生成されたパスワードをメモ

詳細: https://support.google.com/accounts/answer/185833

### 2. 環境変数の設定

`backend/.env`ファイルを編集して、実際の認証情報を設定してください：

```bash
# Gmail Settings
GMAIL_EMAIL=your-actual-email@gmail.com
GMAIL_PASSWORD=your-app-password-here
```

⚠️ **重要**: 通常のGmailパスワードではなく、アプリパスワードを使用してください。

### 3. 依存関係のインストール

```bash
cd backend
pip install -r requirements.txt
```

## テスト方法

### 方法1: シンプルな接続テスト

最も基本的なGmail接続テストです：

```bash
cd backend
python simple_gmail_test.py
```

このテストでは以下を確認します：
- Gmail IMAP接続
- 認証
- メール数の取得
- 最新未読メールの表示

### 方法2: 完全なポーリングテスト

実際のメールポーリング機能をテストします：

```bash
cd backend
python test_gmail_polling.py
```

このテストでは以下を確認します：
- ストレージディレクトリの作成
- Gmail接続
- メールポーリング処理
- ファイル保存機能
- PDF添付ファイル処理

### 方法3: FastAPIサーバー経由でのテスト

実際のAPIサーバーを起動してテストします：

```bash
cd backend
python -m app.main
```

サーバー起動後、以下のエンドポイントにアクセス：
- API文書: http://localhost:8000/api/docs
- メールポーリング実行: POST http://localhost:8000/api/v1/emails/poll

## テスト結果の確認

### 成功時の出力例

```
🚀 Gmailポーリングテスト開始

=== ストレージディレクトリテスト ===
✅ ディレクトリ確認: ./storage
✅ ディレクトリ確認: ./storage/emails
✅ ディレクトリ確認: ./storage/pdfs

=== Gmail接続テスト ===
Gmail Email: your-email@gmail.com
Gmail IMAP Server: imap.gmail.com
Gmail IMAP Port: 993
Password設定: 設定済み

✅ Gmail接続成功!
   総メール数: 1234
   未読メール数: 5

=== メールポーリングテスト ===
✅ ポーリング成功!
   処理したメール数: 2
   処理されたメール:
     - ID: 12345
       件名: テストメール
       PDF数: 1

🎉 テスト完了!
```

### エラー時の対処法

#### 認証エラー
```
❌ IMAP認証エラー: [AUTHENTICATIONFAILED] Invalid credentials
```
- メールアドレスとアプリパスワードを確認
- 2段階認証が有効になっているか確認
- アプリパスワードが正しく生成されているか確認

#### 接続エラー
```
❌ 接続エラー: [Errno 61] Connection refused
```
- インターネット接続を確認
- ファイアウォール設定を確認
- IMAP設定（サーバー、ポート）を確認

## ファイル構成

テスト実行後、以下のディレクトリ構造が作成されます：

```
backend/
├── storage/
│   ├── emails/          # 受信したメールファイル(.eml)
│   └── pdfs/           # 抽出されたPDFファイル
├── test_gmail_polling.py    # 完全テストスクリプト
├── simple_gmail_test.py     # シンプルテストスクリプト
└── .env                     # 環境変数設定
```

## トラブルシューティング

### よくある問題

1. **アプリパスワードが機能しない**
   - 2段階認証が有効になっているか確認
   - アプリパスワードを再生成してみる

2. **未読メールが処理されない**
   - メールが実際に未読状態か確認
   - 他のメールクライアントで既読にしていないか確認

3. **PDF添付ファイルが見つからない**
   - テスト用にPDF添付ファイル付きのメールを送信
   - ファイル権限を確認

### デバッグ情報の確認

詳細なログを確認したい場合は、環境変数を設定：

```bash
export DEBUG=true
python test_gmail_polling.py
```

## セキュリティ注意事項

- `.env`ファイルをGitにコミットしないでください
- アプリパスワードは安全に管理してください
- 本番環境では適切な暗号化を実装してください

## 次のステップ

テストが成功したら：
1. スケジューラーの動作確認
2. 他のサービス（Notion、Dify等）との連携テスト
3. エラーハンドリングの改善
4. ログ機能の追加
