import asyncio
from app.services.email_service import EmailService
from app.services.x_api_service import XApiService
from app.services.dify_service import DifyService
from app.services.notion_service import NotionService


async def process_email_with_apis(email_data: dict, x_api_service: XApiService, dify_service: DifyService, notion_service: NotionService, email_service: EmailService):
    """メールデータを外部APIで処理"""
    email_info = email_data["email_info"]
    pdf_files = email_data["pdf_files"]
    email_id = email_data["email_id"]
    
    # 処理成功フラグ
    all_pdfs_processed = True
    
    # 各PDFファイルを処理
    for pdf_file in pdf_files:
        try:
            print(f"PDF {pdf_file} の処理を開始します...")
            
            # X-APIにアップロード
            print("X-APIにファイルをアップロード中...")
            upload_result = await x_api_service.upload_pdf(pdf_file)
            
            if upload_result.get("status") == "success":
                print("✅ X-APIアップロード成功!")
                upload_data = upload_result.get("data", {})
                print(f"X-API結果構造: {upload_result}")
                if "url" in upload_data:
                    print(f"🔗 アップロードURL: {upload_data['url']}")
                    print(f"📅 有効期限: {upload_data.get('end_datetime', 'N/A')}")

            else:
                print(f"❌ X-APIアップロード失敗: {upload_result.get('message')}")
            
            # DifyでOCR処理
            print("DifyでOCR処理を開始...")
            # ファイルアップロード
            file_id = await dify_service.upload_file(pdf_file)
            print(f"Difyファイルアップロード完了: {file_id}")
            
            # OCR処理（PDFファイルなので file_type を "document" に指定）
            ocr_result = await dify_service.process_ocr(file_id, file_type="document")
            print(f"OCR結果: {ocr_result}")
            
            # OCR結果からvendor情報を抽出して曖昧検索を実行
            vendor = ""
            if isinstance(ocr_result, dict) and "result" in ocr_result:
                result_data = ocr_result["result"]
                if isinstance(result_data, dict) and "data" in result_data:
                    data_list = result_data["data"]
                    if isinstance(data_list, list) and len(data_list) > 0:
                        first_item = data_list[0]
                        if isinstance(first_item, dict):
                            vendor = first_item.get("vendor", "")
            
            # vendorが存在する場合、曖昧検索を実行
            fuzzy_search_result = None
            if vendor:
                print(f"クライアント曖昧検索を実行中: {vendor}")
                
                # NotionからクライアントDBの全データを取得
                all_clients = await notion_service.get_all_clients()
                
                if all_clients:
                    # クライアント情報をDifyに送信しやすい形式に変換
                    notion_clients_for_dify = [
                        {
                            "id": client["id"],
                            "name": client["name"],
                            "abbreviation": client["abbreviation"]
                        }
                        for client in all_clients
                    ]
                    
                    # Difyで曖昧検索を実行
                    fuzzy_search_result = await dify_service.search_client_fuzzy(
                        vendor,
                        notion_clients_for_dify
                    )
                    print(f"曖昧検索結果: {fuzzy_search_result}")
            
            # Notionに登録
            notion_result = await notion_service.create_entry({
                **email_info,
                "pdf_file": pdf_file,
                "x_api_result": upload_result,
                "ocr_result": ocr_result,
                "fuzzy_search_result": fuzzy_search_result  # 曖昧検索結果も含める
            })
            
            if notion_result.get("status") == "success":
                print(f"✅ Notion登録成功: {notion_result.get('url')}")
                
                # 処理成功したPDFファイルを削除
                if await email_service.delete_pdf_file(pdf_file):
                    print(f"✅ PDFファイルを削除しました: {pdf_file}")
                else:
                    print(f"⚠️ PDFファイルの削除に失敗しました: {pdf_file}")
            else:
                print(f"❌ Notion登録失敗: {notion_result.get('message')}")
                all_pdfs_processed = False
            
            print(f"✅ PDF {pdf_file} の外部API処理が完了しました")
            
        except Exception as e:
            print(f"PDF {pdf_file} の外部API処理でエラーが発生しました: {e}")
            all_pdfs_processed = False
    
    # すべてのPDFが正常に処理された場合、メールファイルも削除
    if all_pdfs_processed and pdf_files:
        if await email_service.delete_email_file(email_id):
            print(f"✅ メールファイルを削除しました: {email_id}.eml")
        else:
            print(f"⚠️ メールファイルの削除に失敗しました: {email_id}.eml")


def execute_email_polling_job():
    """メールポーリングジョブを実行"""
    try:
        print("メールポーリングジョブを開始します...")
        
        # 非同期関数を同期的に実行
        email_service = EmailService()
        result = asyncio.run(email_service.poll_emails())
        
        if "error" in result:
            print(f"メールポーリングでエラーが発生しました: {result['error']}")
            return
        
        print(f"メール取得完了: {result['processed_count']}件のメールを処理しました")
        
        # 外部API連携サービスを初期化
        x_api_service = XApiService()
        dify_service = DifyService()
        notion_service = NotionService()
        
        # 取得したメールデータを外部APIで処理
        processed_emails = result.get("emails", [])
        
        async def process_all_emails():
            for email_data in processed_emails:
                if email_data["pdf_files"]:  # PDFファイルがある場合のみ処理
                    await process_email_with_apis(email_data, x_api_service, dify_service, notion_service, email_service)
                else:
                    print(f"メールID {email_data['email_id']} にはPDFファイルが含まれていません。スキップします。")
        
        # 外部API処理を実行
        if processed_emails:
            asyncio.run(process_all_emails())
            print(f"外部API連携処理が完了しました")
        else:
            print("処理対象のメールがありませんでした")
            
    except Exception as e:
        print(f"メールポーリングジョブでエラーが発生しました: {e}")
