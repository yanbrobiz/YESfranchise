FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# 安裝時區資料
RUN apt-get update && apt-get install -y tzdata && rm -rf /var/lib/apt/lists/*

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY . .

# 設定時區為台北
ENV TZ=Asia/Taipei
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# 執行主程式
CMD ["python", "main.py"]
