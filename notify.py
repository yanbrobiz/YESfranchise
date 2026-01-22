"""
LINE Messaging API 通知模組
用於發送自動化執行失敗通知
"""

import os
import requests


def send_line_message(message: str) -> bool:
    """
    透過 LINE Messaging API 發送訊息

    需要設定環境變數：
    - LINE_CHANNEL_TOKEN: LINE Official Account 的 Channel Access Token
    - LINE_USER_ID: 要接收通知的用戶 ID

    Args:
        message: 要發送的訊息內容

    Returns:
        bool: 發送成功返回 True，失敗返回 False
    """
    token = os.environ.get("LINE_CHANNEL_TOKEN")
    user_id = os.environ.get("LINE_USER_ID")

    if not token:
        print("[通知] 未設定 LINE_CHANNEL_TOKEN 環境變數，跳過通知")
        return False

    if not user_id:
        print("[通知] 未設定 LINE_USER_ID 環境變數，跳過通知")
        return False

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            print("[通知] LINE 訊息發送成功")
            return True
        else:
            print(f"[通知] LINE 訊息發送失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[通知] LINE 訊息發送錯誤: {e}")
        return False


def notify_failure(error_message: str):
    """
    發送執行失敗通知

    Args:
        error_message: 錯誤訊息
    """
    message = f"""Yes!加盟 自動化執行失敗

錯誤訊息: {error_message}

請檢查 Railway 日誌確認詳細錯誤。"""
    send_line_message(message)
