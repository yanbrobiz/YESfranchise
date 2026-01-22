FROM mcr.microsoft.com/playwright/python:v1.57.0-jammy

WORKDIR /app

# 關閉 Python 輸出緩衝，確保日誌即時顯示
ENV PYTHONUNBUFFERED=1

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 執行主程式
CMD ["python", "-u", "main.py"]
