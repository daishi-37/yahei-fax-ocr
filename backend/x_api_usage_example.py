"""
X-API ファイルアップロード機能の使用例

このファイルは、X-APIサービスを使用してファイルをアップロードする
様々な方法を示すサンプルコードです。
"""

import asyncio
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.append(str(Path(__file__).parent))

from app.services.x_api_service import XApiService


async def basic_file_upload_example():
    """基本的なファイルアップロードの例"""
    
    print("=== 基本的なファイルアップロード例 ===")
    
    # X-APIサービスのインスタンス作成
    x_api = XApiService()
    
    # ファイルパスを指定してアップロード
    file_path = "path/to/your/file.pdf"  # 実際のファイルパスに変更してください
    
    try:
        result = await x_api.upload_file(
            file_path=file_path,
            expire_hours=24  # 24時間後に期限切れ
        )
        
        if result["status"] == "success":
            print("✅ アップロード成功!")
            print(f"メッセージ: {result['message']}")
            
            # レスポンスデータの表示
            data = result.get("data", {})
            print(f"ファイルID: {data.get('data')}")
            print(f"URL: {data.get('url')}")
            print(f"開始日時: {data.get('start_datetime')}")
            print(f"終了日時: {data.get('end_datetime')}")
            
        else:
            print("❌ アップロード失敗")
            print(f"エラー: {result['message']}")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")


async def pdf_upload_example():
    """PDFファイル専用アップロードの例（既存コードとの互換性）"""
    
    print("\n=== PDFファイルアップロード例 ===")
    
    x_api = XApiService()
    
    pdf_path = "path/to/your/document.pdf"  # 実際のPDFファイルパスに変更してください
    
    try:
        result = await x_api.upload_pdf(
            pdf_file_path=pdf_path,
            expire_hours=48  # 48時間後に期限切れ
        )
        
        if result["status"] == "success":
            print("✅ PDFアップロード成功!")
            
            # ファイル情報の抽出
            file_info = x_api.get_file_info(result)
            if file_info:
                print("📄 ファイル情報:")
                for key, value in file_info.items():
                    print(f"  {key}: {value}")
        else:
            print("❌ PDFアップロード失敗")
            print(f"エラー: {result['message']}")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")


async def batch_upload_example():
    """複数ファイルの一括アップロード例"""
    
    print("\n=== 複数ファイル一括アップロード例 ===")
    
    x_api = XApiService()
    
    # アップロードするファイルのリスト
    files_to_upload = [
        {"path": "file1.pdf", "expire_hours": 24},
        {"path": "file2.jpg", "expire_hours": 48},
        {"path": "file3.txt", "expire_hours": 12},
    ]
    
    upload_results = []
    
    for file_info in files_to_upload:
        try:
            print(f"📤 アップロード中: {file_info['path']}")
            
            result = await x_api.upload_file(
                file_path=file_info["path"],
                expire_hours=file_info["expire_hours"]
            )
            
            upload_results.append({
                "file": file_info["path"],
                "result": result
            })
            
            if result["status"] == "success":
                print(f"✅ {file_info['path']} - アップロード成功")
            else:
                print(f"❌ {file_info['path']} - アップロード失敗: {result['message']}")
                
        except Exception as e:
            print(f"❌ {file_info['path']} - エラー: {str(e)}")
            upload_results.append({
                "file": file_info["path"],
                "result": {"status": "error", "message": str(e)}
            })
    
    # 結果のサマリー
    print("\n📊 アップロード結果サマリー:")
    success_count = sum(1 for r in upload_results if r["result"]["status"] == "success")
    total_count = len(upload_results)
    print(f"成功: {success_count}/{total_count}")
    
    return upload_results


async def error_handling_example():
    """エラーハンドリングの例"""
    
    print("\n=== エラーハンドリング例 ===")
    
    x_api = XApiService()
    
    # 存在しないファイルのアップロードを試行
    non_existent_file = "non_existent_file.pdf"
    
    result = await x_api.upload_file(non_existent_file)
    
    if result["status"] == "error":
        print("⚠️ 予期されたエラーが発生しました:")
        print(f"メッセージ: {result['message']}")
        
        # エラーの種類に応じた処理
        if "ファイルが見つかりません" in result["message"]:
            print("💡 対処法: ファイルパスを確認してください")
        elif "タイムアウト" in result["message"]:
            print("💡 対処法: ネットワーク接続を確認してください")
        elif "API接続エラー" in result["message"]:
            print("💡 対処法: APIサーバーの状態を確認してください")


async def configuration_example():
    """設定情報の確認例"""
    
    print("\n=== 設定情報確認例 ===")
    
    x_api = XApiService()
    
    print("🔧 現在の設定:")
    print(f"API URL: {x_api.base_url}")
    print(f"API Key: {'設定済み' if x_api.api_key else '未設定'}")
    
    if x_api.api_key:
        print(f"API Key (先頭20文字): {x_api.api_key[:20]}...")
    else:
        print("⚠️ API Keyが設定されていません。.envファイルを確認してください。")


async def main():
    """メイン実行関数"""
    
    print("🚀 X-API ファイルアップロード使用例\n")
    
    # 設定確認
    await configuration_example()
    
    # 基本的なアップロード例
    await basic_file_upload_example()
    
    # PDFアップロード例
    await pdf_upload_example()
    
    # 一括アップロード例
    await batch_upload_example()
    
    # エラーハンドリング例
    await error_handling_example()
    
    print("\n✨ 使用例の実行が完了しました")
    print("\n📝 注意事項:")
    print("- 実際に使用する際は、ファイルパスを正しいものに変更してください")
    print("- .envファイルでX_API_URLとX_API_KEYが正しく設定されていることを確認してください")
    print("- ファイルサイズやAPIの制限に注意してください")


if __name__ == "__main__":
    asyncio.run(main())
