# 🎮 Game Oẳn Tù Tì - Web Version

Game Oẳn Tù Tì (Rock-Paper-Scissors) multiplayer chơi trên trình duyệt web với WebSocket real-time.

---

## 📋 Tổng quan

Game cho phép 2 người chơi kết nối qua browser và chơi Oẳn Tù Tì real-time. Server tự động ghép cặp người chơi.

### ✨ Tính năng

- ✅ **Multiplayer real-time** với WebSocket
- ✅ **Chơi trên browser** - không cần cài đặt
- ✅ **Cross-platform** - PC, mobile, tablet
- ✅ **Tự động matchmaking** - ghép cặp tự động
- ✅ **Dark theme UI** - giao diện đẹp mắt
- ✅ **Responsive design** - tương thích mọi màn hình

### 🎯 Luật chơi

- ✊ **Búa** thắng **Kéo**
- ✋ **Bao** thắng **Búa**
- ✌️ **Kéo** thắng **Bao**

---

## 🚀 Cài đặt

### Yêu cầu

- **Python 3.7+**

### Cài đặt Dependencies

```bash
cd Rock-Paper-Scissors

pip install -r requirements.txt
```

---

## 🎮 Cách chơi

### Bước 1: Khởi động Server

```bash
python web_server.py
```

Bạn sẽ thấy:

```
============================================================
🌐 Rock-Paper-Scissors Web Server
============================================================
Server starting on http://localhost:5000
============================================================
```

### Bước 2: Mở Browser

Mở **2 tabs** hoặc **2 browsers**:

- Tab 1: http://localhost:5000
- Tab 2: http://localhost:5000

### Bước 3: Tìm trận & Chơi

1. Cả 2 tabs click **"🔌 Tìm trận"**
2. Khi ghép cặp thành công, chọn nước đi (Búa/Bao/Kéo)
3. Xem kết quả ngay lập tức
4. Click **"🔄 Tìm trận mới"** để chơi tiếp

---

## 📁 Cấu trúc dự án

```
Rock-Paper-Scissors/
├── web_server.py          # Flask-SocketIO server
├── game_protocol.py       # Game logic & constants
├── templates/
│   └── index.html         # Web UI
├── static/
│   ├── css/
│   │   └── style.css      # Dark theme styling
│   └── js/
│       └── game.js        # WebSocket client
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🔧 Chơi từ xa qua LAN (Cùng WiFi)

### LAN là gì?

**LAN** = **Local Area Network** (Mạng cục bộ)

**Chơi qua LAN** có nghĩa:

- 🏠 **2 người ở 2 máy tính khác nhau**
- 📶 **Cùng 1 mạng WiFi** (ví dụ: WiFi nhà, WiFi công ty)
- 🚫 **KHÔNG cần internet** - chỉ cần WiFi local

### Ví dụ minh họa:

```
🏠 Nhà bạn - Router WiFi "MyHome"
│
├── 💻 Máy 1 (Bạn)
│   IP: 192.168.1.100
│   Vai trò: Chạy server
│   Truy cập: http://localhost:5000
│
└── 💻 Máy 2 (Bạn bè/Gia đình)
    IP: 192.168.1.101
    Vai trò: Chơi game
    Truy cập: http://192.168.1.100:5000
```

**→ Cả 2 máy chơi được với nhau!**

---

### Hướng dẫn chi tiết:

#### Bước 1: Tìm IP của máy chạy server

**Trên máy chạy server (Máy 1):**

**Windows:**

```bash
ipconfig
```

Tìm dòng "IPv4 Address" → Ví dụ: `192.168.1.100`

**Mac/Linux:**

```bash
ifconfig | grep "inet "
```

**Ví dụ output:**

```
Wireless LAN adapter Wi-Fi:
   IPv4 Address: 192.168.1.100  ← Đây là IP của bạn!
```

#### Bước 2: Chạy server

```bash
python web_server.py
```

Server sẽ lắng nghe trên **tất cả network interfaces** (`0.0.0.0:5000`)

#### Bước 3: Kết nối từ máy khác

Trên **Máy 2** (trong cùng WiFi), mở browser:

```
http://192.168.1.100:5000
```

✅ **Thay `192.168.1.100` bằng IP của Máy 1!**

---

### Troubleshooting

**❌ Problem: Không kết nối được**

**Giải pháp:**

1. **Kiểm tra firewall:**
   - Windows: Cho phép Python qua Windows Firewall
   - Mac: System Preferences → Security & Privacy → Firewall
   - Hoặc tắt firewall tạm thời để test

2. **Cùng WiFi:**
   - Đảm bảo cả 2 máy cùng WiFi/Router
   - KHÔNG dùng Mobile Hotspot riêng

3. **Test ping:**

   ```bash
   ping 192.168.1.100
   ```

   - Nếu ping được → Network OK
   - Nếu không ping được → Vấn đề mạng

4. **Check server logs:**
   - Xem terminal chạy server
   - Có thấy connection request không?

---

## 🔧 WebSocket Protocol

### Client → Server

```javascript
socket.emit("find_match");
socket.emit("send_move", { move: "ROCK" });
```

### Server → Client

```javascript
socket.on("waiting");
socket.on("match_found");
socket.on("game_result", {
  result: "WIN",
  your_move: "ROCK",
  opponent_move: "SCISSORS",
});
```

---

## 🐛 Troubleshooting

### Port 5000 đang được sử dụng

```
Error: Address already in use
```

**Giải pháp:**

- Tắt server cũ (Ctrl+C)
- Hoặc đổi port trong `web_server.py`: `socketio.run(app, port=5001)`

### Không kết nối được

- ✅ Kiểm tra server đã chạy
- ✅ Refresh browser (Ctrl+F5)
- ✅ Check console logs (F12 → Console)
- ✅ Kiểm tra firewall

### Dependencies lỗi

```bash
pip install --upgrade Flask Flask-SocketIO
```

---

## 📝 Ghi chú kỹ thuật

**Technology Stack:**

- **Backend:** Flask + Flask-SocketIO
- **Frontend:** HTML5 + CSS3 + Vanilla JS
- **Real-time:** Socket.IO (WebSocket)
- **Styling:** Dark theme với gradients

**Game Logic:**

- Tất cả logic game trong `game_protocol.py`
- Server chỉ làm matchmaking và route messages
- Client render UI và handle user input

---

## 🎓 Tính năng nâng cao

### Customize màu sắc

Chỉnh sửa `static/css/style.css`:

```css
/* Đổi màu background */
body {
  background: linear-gradient(135deg, #yourcolor1, #yourcolor2);
}
```

### Đổi port server

Trong `web_server.py`:

```python
socketio.run(app, host='0.0.0.0', port=YOUR_PORT)
```

---

**🎉 Chúc bạn chơi game vui vẻ!**

_Made with ❤️ using Flask & Socket.IO_
