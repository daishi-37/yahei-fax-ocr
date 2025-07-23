#!/usr/bin/env python3
"""
シンプルなGmail接続テスト
"""
import imaplib
import os
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

def test_gmail_connection():
    """Gmail接続の基本テスト"""
    
    # 環境変数から設定を取得
    email = os.getenv("GMAIL_EMAIL")
    password = os.getenv("GMAIL_PASSWORD")
    server = os.getenv("GMAIL_IMAP_SERVER", "imap.gmail.com")
    port = int(os.getenv("GMAIL_IMAP_PORT", "993"))
    
    print("=== Gmail接続テスト ===")
    print(f"Email: {email}")
    print(f"Server: {server}")
    print(f"Port: {port}")
    print(f"Password: {'設定済み' if password else '未設定'}")
    print()
    
    if not email or not password:
        print("❌ Gmail設定が不完全です。")
        print("   .envファイルでGMAIL_EMAILとGMAIL_PASSWORDを設定してください。")
        return False
    
    try:
        print("Gmail IMAPサーバーに接続中...")
        mail = imaplib.IMAP4_SSL(server, port)
        
        print("ログイン中...")
        mail.login(email, password)
        
        print("受信箱を選択中...")
        mail.select('inbox')
        
        # メール数を確認
        print("メール数を確認中...")
        status, messages = mail.search(None, 'ALL')
        total_emails = len(messages[0].split()) if messages[0] else 0
        
        status, unread_messages = mail.search(None, 'UNSEEN')
        unread_count = len(unread_messages[0].split()) if unread_messages[0] else 0
        
        print("✅ Gmail接続成功!")
        print(f"   総メール数: {total_emails}")
        print(f"   未読メール数: {unread_count}")
        
        # 最新の未読メールの件名を表示（あれば）
        if unread_count > 0:
            print("\n最新の未読メール:")
            # 最新の未読メール1件を取得
            email_id = unread_messages[0].split()[-1]  # 最後のメールID
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            
            import email
            email_message = email.message_from_bytes(msg_data[0][1])
            subject = email_message.get("Subject", "件名なし")
            from_addr = email_message.get("From", "送信者不明")
            
            print(f"   件名: {subject}")
            print(f"   送信者: {from_addr}")
        
        mail.close()
        mail.logout()
        
        return True
        
    except imaplib.IMAP4.error as e:
        print(f"❌ IMAP認証エラー: {e}")
        print("   - メールアドレスとパスワードを確認してください")
        print("   - Gmailの2段階認証が有効な場合は、アプリパスワードを使用してください")
        print("   - https://support.google.com/accounts/answer/185833")
        return False
        
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        return False


if __name__ == "__main__":
    success = test_gmail_connection()
    
    if success:
        print("\n🎉 テスト完了! Gmailポーリングの準備ができています。")
    else:
        print("\n❌ テスト失敗。設定を確認してください。")
