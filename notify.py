"""
LINE Notify 通知模組
用於發送自動化執行失敗通知
"""

import os
import requests


def send_line_notify(message: str) -> bool:
    """
    發送 LINE Notify 通知

    Args:
        message: 要發送的訊息內容

    Returns:
        bool: 發送成功返回 True，失敗返回 False
    """
    token = os.environ.get("LINE_NOTIFY_TOKEN")

    if not token:
        print("[通知] 未設定 LINE_NOTIFY_TOKEN 環境變數，跳過通知")
        return False

    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    data = {
        "message": message
    }

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            print("[通知] LINE Notify 發送成功")
            return True
        else:
            print(f"[通知] LINE Notify 發送失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[通知] LINE Notify 發送錯誤: {e}")
        return False


def notify_failure(error_message: str):
    """
    發送執行失敗通知

    Args:
        error_message: 錯誤訊息
    """
    message = f"""
Yes!加盟 自動化執行失敗

錯誤訊息: {error_message}

請檢查 Railway 日誌確認詳細錯誤。
"""
    send_line_notify(message)
