import time
import psutil
from flask import Flask, render_template, jsonify
from datetime import datetime

app = Flask(__name__)

def get_process_name(pid):
    """Lấy tên tiến trình từ PID, xử lý trường hợp tiến trình đã đóng hoặc không có quyền."""
    try:
        process = psutil.Process(pid)
        return process.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return "Unknown/System"

def get_network_activity():
    """
    Thu thập danh sách các kết nối mạng hiện tại.
    Sử dụng psutil.net_connections() tương đương với lệnh netstat.
    """
    connections = []
    
    # Lấy tất cả kết nối inet (IPv4, IPv6) cả TCP và UDP
    # Cần quyền Admin/Root để thấy PID của các process hệ thống
    try:
        # kind='inet' lọc IPv4/IPv6. Có thể dùng 'all' nếu muốn cả UNIX sockets
        net_conns = psutil.net_connections(kind='inet')
    except psutil.AccessDenied:
        # Fallback nếu không có quyền root, chỉ lấy được kết nối của user hiện tại
        net_conns = psutil.net_connections(kind='inet')

    for conn in net_conns:
        # Định dạng địa chỉ IP:Port
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}"
        raddr = ""
        if conn.raddr:
            raddr = f"{conn.raddr.ip}:{conn.raddr.port}"
        
        # Xác định giao thức (TCP/UDP) dựa trên loại socket
        protocol = "TCP" if conn.type == 1 else "UDP" # 1=SOCK_STREAM, 2=SOCK_DGRAM

        # Chỉ lấy các trạng thái quan trọng để đỡ rối mắt
        # Hoặc lấy hết nếu cần. UDP thường trạng thái là NONE.
        status = conn.status
        
        # Tạo object log
        log_entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "pid": conn.pid,
            "process_name": get_process_name(conn.pid) if conn.pid else "System",
            "protocol": protocol,
            "laddr": laddr,
            "raddr": raddr or "*", # Nếu không có remote address (vd: đang Listen)
            "status": status
        }
        connections.append(log_entry)

    # Sắp xếp: Ưu tiên kết nối ESTABLISHED, sau đó đến mới nhất
    connections.sort(key=lambda x: (x['status'] != 'ESTABLISHED', x['process_name']))
    
    return connections

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/activity')
def api_activity():
    """API trả về dữ liệu JSON cho Frontend fetch"""
    data = get_network_activity()
    return jsonify(data)

if __name__ == '__main__':
    # Chạy server. debug=True giúp auto-reload khi sửa code
    print("[-] Server đang chạy tại http://127.0.0.1:5000")
    print("[-] Lưu ý: Chạy với quyền Administrator/Sudo để xem đầy đủ tên tiến trình hệ thống.")
    # app.run(debug=True, port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000) # Để có thể chạy được trên Docker