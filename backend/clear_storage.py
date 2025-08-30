import os
import shutil
import json
from datetime import datetime

def clear_storage():
    """
    監視メールアドレス変更に伴い、過去のデータを削除するスクリプト
    """
    # ストレージパスの設定
    storage_path = "./storage"
    email_storage_path = f"{storage_path}/emails"
    pdf_storage_path = f"{storage_path}/pdfs"
    
    # 削除前の状態を記録
    deleted_files = {
        "json_files": [],
        "email_files": [],
        "pdf_files": []
    }
    
    # 1. JSONファイルの削除（processed_email_ids.json, last_poll_time.json）
    json_files = ["processed_email_ids.json", "last_poll_time.json"]
    for json_file in json_files:
        json_path = f"{storage_path}/{json_file}"
        if os.path.exists(json_path):
            # バックアップを作成
            backup_path = f"{json_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(json_path, backup_path)
            print(f"バックアップを作成しました: {backup_path}")
            
            # ファイルを削除
            os.remove(json_path)
            deleted_files["json_files"].append(json_file)
            print(f"JSONファイルを削除しました: {json_file}")
    
    # 2. メールファイルの削除
    if os.path.exists(email_storage_path):
        email_files = os.listdir(email_storage_path)
        for email_file in email_files:
            if email_file.endswith(".eml"):
                email_path = f"{email_storage_path}/{email_file}"
                os.remove(email_path)
                deleted_files["email_files"].append(email_file)
        print(f"メールファイルを削除しました: {len(deleted_files['email_files'])}件")
    
    # 3. PDFファイルの削除
    if os.path.exists(pdf_storage_path):
        pdf_files = os.listdir(pdf_storage_path)
        for pdf_file in pdf_files:
            if pdf_file.endswith(".pdf"):
                pdf_path = f"{pdf_storage_path}/{pdf_file}"
                os.remove(pdf_path)
                deleted_files["pdf_files"].append(pdf_file)
        print(f"PDFファイルを削除しました: {len(deleted_files['pdf_files'])}件")
    
    # 削除結果のサマリーを作成
    summary = {
        "timestamp": datetime.now().isoformat(),
        "deleted_files": {
            "json_files_count": len(deleted_files["json_files"]),
            "email_files_count": len(deleted_files["email_files"]),
            "pdf_files_count": len(deleted_files["pdf_files"]),
            "total_count": len(deleted_files["json_files"]) + len(deleted_files["email_files"]) + len(deleted_files["pdf_files"])
        }
    }
    
    # 削除結果のサマリーを保存
    with open(f"{storage_path}/clear_summary.json", "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print("\n削除処理が完了しました")
    print(f"JSONファイル: {len(deleted_files['json_files'])}件")
    print(f"メールファイル: {len(deleted_files['email_files'])}件")
    print(f"PDFファイル: {len(deleted_files['pdf_files'])}件")
    print(f"合計: {summary['deleted_files']['total_count']}件")
    print(f"\n削除結果のサマリーを保存しました: {storage_path}/clear_summary.json")

if __name__ == "__main__":
    # 確認メッセージを表示
    print("監視メールアドレス変更に伴い、過去のデータを削除します。")
    print("この操作は元に戻せません。続行しますか？ [y/N]")
    
    confirmation = input().strip().lower()
    if confirmation == "y":
        clear_storage()
    else:
        print("削除処理をキャンセルしました。")
