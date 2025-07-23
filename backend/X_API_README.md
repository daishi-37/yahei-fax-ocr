# X-API ファイルアップロード機能

このドキュメントでは、X-APIを使用したファイルアップロード機能の実装と使用方法について説明します。

## 概要

X-APIは、ファイルをアップロードして一時的なURLを生成するサービスです。アップロードされたファイルには有効期限を設定でき、指定した時間後に自動的に削除されます。

## API仕様

- **エンドポイント**: `POST /x-api/api/v1/upload/`
- **認証**: Bearer Token
- **Content-Type**: `multipart/form-data`

### リクエストパラメータ

| パラメータ | 型 | 必須 | 説明 |
|-----------|---|------|------|
| file | binary | ✅ | アップロードするファイル |
| expire_hours | integer | ✅ | ファイルの有効期限（時間） |

### レスポンス

#### 成功時 (200)
```json
{
  "data": "123e4567-e89b-12d3-a456-426614174000",
  "title": "123e4567-e89b-12d3-a456-426614174000.jpg",
  "url": "https://example.com/x-api/uploads/123e4567-e89b-12d3-a456-426614174000.jpg",
  "start_datetime": "2025-03-06T12:14:25:00",
  "end_datetime": "2025-03-07T12:14:25:00"
}
```

#### エラー時 (422)
```json
{
  "detail": [
    {
      "loc": ["string"],
      "msg": "string",
      "type": "string"
    }
  ]
}
```

## 設定

### 環境変数

`.env`ファイルに以下の設定を追加してください：

```env
# X-API Settings
X_API_URL=https://p00-log001a.rsf-node001.com/x-api/api/v1/upload/
X_API_KEY=your-jwt-token-here
```

### 設定ファイル

`app/core/settings.py`で設定が読み込まれます：

```python
X_API_URL = os.getenv("X_API_URL")
X_API_KEY = os.getenv("X_API_KEY")
```

## 使用方法

### 基本的な使用例

```python
from app.services.x_api_service import XApiService

# サービスのインスタンス作成
x_api = XApiService()

# ファイルアップロード
result = await x_api.upload_file(
    file_path="path/to/your/file.pdf",
    expire_hours=24  # 24時間後に期限切れ
)

if result["status"] == "success":
    print("アップロード成功!")
    data = result["data"]
    print(f"ファイルURL: {data['url']}")
else:
    print(f"アップロード失敗: {result['message']}")
```

### PDFファイル専用メソッド

既存コードとの互換性のため、PDF専用メソッドも提供されています：

```python
# PDFファイルのアップロード
result = await x_api.upload_pdf(
    pdf_file_path="document.pdf",
    expire_hours=48
)
```

### ファイル情報の抽出

アップロード結果からファイル情報を抽出できます：

```python
file_info = x_api.get_file_info(result)
if file_info:
    print(f"ファイルID: {file_info['file_id']}")
    print(f"URL: {file_info['url']}")
    print(f"開始日時: {file_info['start_datetime']}")
    print(f"終了日時: {file_info['end_datetime']}")
```

## エラーハンドリング

サービスは以下のエラーを適切にハンドリングします：

### ファイル関連エラー
- ファイルが存在しない
- ファイルの読み込みエラー

### ネットワーク関連エラー
- 接続タイムアウト
- API接続エラー

### API関連エラー
- 認証エラー
- バリデーションエラー
- サーバーエラー

### エラーレスポンス例

```python
{
    "status": "error",
    "message": "ファイルが見つかりません: /path/to/file.pdf"
}

{
    "status": "error",
    "status_code": 422,
    "message": "アップロードに失敗しました: Validation Error",
    "response": "詳細なエラーメッセージ"
}
```

## テスト

### テストファイルの実行

```bash
# X-APIサービスのテスト
cd backend
python test_x_api_service.py

# 使用例の実行
python x_api_usage_example.py
```

### テスト内容

1. **基本的なファイルアップロードテスト**
   - テストファイルの作成とアップロード
   - レスポンスデータの検証

2. **PDF互換性テスト**
   - 既存メソッドとの互換性確認

3. **エラーハンドリングテスト**
   - 存在しないファイルのテスト
   - ネットワークエラーのテスト

## ファイル構成

```
backend/
├── app/
│   ├── services/
│   │   └── x_api_service.py          # X-APIサービス実装
│   └── core/
│       └── settings.py               # 設定ファイル
├── test_x_api_service.py             # テストファイル
├── x_api_usage_example.py            # 使用例
├── X_API_README.md                   # このドキュメント
└── .env                              # 環境変数設定
```

## クラス・メソッド詳細

### XApiService クラス

#### `__init__()`
サービスの初期化。設定から API URL と API Key を読み込みます。

#### `upload_file(file_path: str, expire_hours: int = 24) -> Dict[str, Any]`
汎用ファイルアップロードメソッド。

**パラメータ:**
- `file_path`: アップロードするファイルのパス
- `expire_hours`: ファイルの有効期限（時間）、デフォルト24時間

**戻り値:**
- 成功時: `{"status": "success", "data": {...}, "message": "..."}`
- 失敗時: `{"status": "error", "message": "...", ...}`

#### `upload_pdf(pdf_file_path: str, expire_hours: int = 24) -> Dict[str, Any]`
PDF専用アップロードメソッド（既存コードとの互換性維持）。

#### `get_file_info(response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]`
アップロードレスポンスからファイル情報を抽出。

## セキュリティ考慮事項

1. **API Key の管理**
   - API Keyは環境変数で管理
   - バージョン管理システムにコミットしない

2. **ファイルサイズ制限**
   - 大きなファイルのアップロード時はタイムアウトに注意
   - 必要に応じてタイムアウト値を調整

3. **ファイル検証**
   - アップロード前にファイルの存在確認
   - 適切なエラーハンドリング

## トラブルシューティング

### よくある問題と解決方法

1. **認証エラー**
   - API Keyが正しく設定されているか確認
   - トークンの有効期限を確認

2. **ファイルアップロードエラー**
   - ファイルパスが正しいか確認
   - ファイルの読み込み権限を確認

3. **ネットワークエラー**
   - API サーバーへの接続を確認
   - プロキシ設定を確認

4. **タイムアウトエラー**
   - ファイルサイズを確認
   - ネットワーク速度を確認
   - タイムアウト値の調整を検討

## 更新履歴

- **2025/7/14**: 初版作成
  - X-API v1 Upload エンドポイント対応
  - ファイルアップロード機能実装
  - エラーハンドリング追加
  - テストコード作成

## 参考資料

- [X-API Swagger Documentation](https://p00-log001a.rsf-node001.com/x-api/api/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Requests Documentation](https://docs.python-requests.org/)
