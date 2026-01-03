# 1. Chọn Base Image: Python phiên bản nhỏ gọn (slim) để nhẹ máy
FROM python:3.9-slim

# 2. Thiết lập thư mục làm việc bên trong Container
WORKDIR /app

# 3. Copy file requirements.txt vào trước để cài thư viện (tận dụng cache của Docker)
COPY requirements.txt .

# 4. Cài đặt các thư viện cần thiết (Flask,...)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ mã nguồn còn lại (app.py, templates,...) vào Container
COPY . .

# 6. Mở cổng 5000 (Cổng mặc định của Flask)
EXPOSE 5000

# 7. Lệnh chạy ứng dụng khi Container khởi động
CMD ["python", "app.py"]