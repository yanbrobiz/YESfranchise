"""
Telegram Bot 通知模組
用於發送自動化執行失敗通知
"""

import os
import requests


def send_telegram_message(message: str) -> bool:
    """
    透過 Telegram Bot 發送訊息

    需要設定環境變數：
    - TELEGRAM_BOT_TOKEN: Bot 的 Token（從 @BotFather 取得）
    - TELEGRAM_CHAT_ID: 要接收通知的 Chat ID

    Args:
        message: 要發送的訊息內容

    Returns:
        bool: 發送成功返回 True，失敗返回 False
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    if not token:
        print("[通知] 未設定 TELEGRAM_BOT_TOKEN 環境變數，跳過通知")
        return False

    if not chat_id:
        print("[通知] 未設定 TELEGRAM_CHAT_ID 環境變數，跳過通知")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("[通知] Telegram 訊息發送成功")
            return True
        else:
            print(f"[通知] Telegram 訊息發送失敗: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[通知] Telegram 訊息發送錯誤: {e}")
        return False


def notify_success():
    """發送執行成功通知"""
    message = "✅ Yes!加盟 自動化執行成功！分館搶先排序已完成。"
    send_telegram_message(message)


def notify_failure(error_message: str):
    """
    發送執行失敗通知

    Args:
        error_message: 錯誤訊息
    """
    message = f"""⚠️ Yes!加盟 自動化執行失敗

錯誤訊息: {error_message}

請檢查 Railway 日誌確認詳細錯誤。"""
    send_telegram_message(message)
