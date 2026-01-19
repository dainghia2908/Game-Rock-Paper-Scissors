"""
Rock-Paper-Scissors Web Server

Web server với Flask-SocketIO cho game Oẳn Tù Tì multiplayer.
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import uuid

from game_protocol import (
    MOVE_ROCK, MOVE_PAPER, MOVE_SCISSORS,
    parse_move_message, determine_winner,
    is_valid_move
)

# Khởi tạo Flask app và SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'rock-paper-scissors-secret-2026'
socketio = SocketIO(app, cors_allowed_origins="*")  # Cho phép CORS từ tất cả origins

# Danh sách players đang chờ ghép cặp
waiting_players = []

# Dictionary lưu thông tin các game đang chơi
# Format: {room_id: {player1_sid, player2_sid, player1_move, player2_move}}
active_games = {}

# Dictionary lưu thông tin players
# Format: {socket_id: {room_id, player_number, name, avatar}}
players = {}

# Dictionary track rematch requests
# Format: {room_id: {player1_ready: bool, player2_ready: bool, player1_sid, player2_sid}}
rematch_requests = {}


@app.route('/')
def index():
    """Render trang chủ game"""
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """
    Xử lý khi client kết nối WebSocket.
    Gửi lại socket ID cho client.
    """
    print(f"[WEB] Client connected: {request.sid}")
    emit('connected', {'sid': request.sid})


@socketio.on('set_player_info')
def handle_set_player_info(data):
    """
    Xử lý khi client gửi thông tin player (name, avatar).
    Lưu vào players dictionary.
    """
    sid = request.sid
    name = data.get('name', 'Player')
    avatar = data.get('avatar', '😀')
    
    print(f"[WEB] Player info set: {sid} - {avatar} {name}")
    
    # Lưu player info (chưa có room_id và player_number)
    if sid not in players:
        players[sid] = {}
    
    players[sid]['name'] = name
    players[sid]['avatar'] = avatar


@socketio.on('disconnect')
def handle_disconnect():
    """
    Xử lý khi client ngắt kết nối.
    - Thông báo cho đối thủ (nếu đang trong game)
    - Xóa khỏi waiting queue
    - Dọn dẹp game state
    """
    sid = request.sid
    print(f"[WEB] Client disconnected: {sid}")
    
    # Kiểm tra xem player có đang trong game không
    if sid in players:
        player_info = players[sid]
        room_id = player_info.get('room_id')
        
        # Nếu đang trong game, thông báo cho đối thủ
        if room_id and room_id in active_games:
            game = active_games[room_id]
            
            # Tìm socket ID của đối thủ
            opponent_sid = game['player1_sid'] if game['player2_sid'] == sid else game['player2_sid']
            
            if opponent_sid:
                emit('opponent_disconnected', room=opponent_sid)
            
            # Xóa game
            del active_games[room_id]
        
        # Xóa player khỏi tracking khi disconnect thật sự
        # (Không xóa sau game kết thúc để có thể rematch)
        if sid in players:
            del players[sid]
    
    # Xóa khỏi waiting queue nếu đang chờ
    if sid in waiting_players:
        waiting_players.remove(sid)


@socketio.on('find_match')
def handle_find_match():
    """
    Xử lý yêu cầu tìm trận đấu.
    - Nếu có người chờ → Ghép cặp ngay
    - Nếu không → Thêm vào waiting queue
    """
    sid = request.sid
    print(f"[WEB] Find match request from: {sid}")
    
    if waiting_players:
        # Có người đang chờ! Ghép cặp ngay
        opponent_sid = waiting_players.pop(0)  # Lấy người đầu tiên trong queue
        
        # Tạo room ID unique cho game này
        room_id = str(uuid.uuid4())
        
        # Lưu thông tin game
        active_games[room_id] = {
            'player1_sid': opponent_sid,
            'player2_sid': sid,
            'player1_move': None,
            'player2_move': None
        }
        
        # Track players - preserve existing name/avatar info
        if opponent_sid in players:
            players[opponent_sid]['room_id'] = room_id
            players[opponent_sid]['player_number'] = 1
        else:
            players[opponent_sid] = {'room_id': room_id, 'player_number': 1}
            
        if sid in players:
            players[sid]['room_id'] = room_id
            players[sid]['player_number'] = 2
        else:
            players[sid] = {'room_id': room_id, 'player_number': 2}
        
        # Cho cả 2 players vào room
        join_room(room_id, sid=opponent_sid)
        join_room(room_id, sid=sid)
        
        print(f"[WEB] Match found! Room {room_id}: {opponent_sid} vs {sid}")
        
        # Lấy thông tin players
        opponent_info = players.get(opponent_sid, {})
        player_info = players.get(sid, {})
        
        # Gửi thông báo kèm opponent info cho cả 2 players
        emit('match_found', {
            'room_id': room_id,
            'opponent_name': player_info.get('name', 'Player 2'),
            'opponent_avatar': player_info.get('avatar', '😎')
        }, room=opponent_sid)
        
        emit('match_found', {
            'room_id': room_id,
            'opponent_name': opponent_info.get('name', 'Player 1'),
            'opponent_avatar': opponent_info.get('avatar', '😀')
        }, room=sid)
        
    else:
        # Chưa có đối thủ, thêm vào queue
        waiting_players.append(sid)
        print(f"[WEB] Player {sid} waiting for opponent...")
        emit('waiting')


@socketio.on('send_move')
def handle_send_move(data):
    """
    Xử lý khi player gửi nước đi.
    
    Flow:
    1. Validate move (ROCK/PAPER/SCISSORS)
    2. Lưu move vào game state
    3. Nếu cả 2 đã chọn → Tính kết quả và gửi về
    4. Clean up game sau khi xong
    """
    sid = request.sid
    move = data.get('move')
    
    print(f"[WEB] Received move from {sid}: {move}")
    
    # Validate move
    if not is_valid_move(move):
        emit('error', {'message': 'Invalid move'})
        return
    
    # Kiểm tra player có đang trong game không
    if sid not in players:
        emit('error', {'message': 'Not in a game'})
        return
    
    player_info = players[sid]
    room_id = player_info['room_id']
    player_number = player_info['player_number']
    
    # Kiểm tra game có tồn tại không
    if room_id not in active_games:
        emit('error', {'message': 'Game not found'})
        return
    
    game = active_games[room_id]
    
    # Lưu move của player
    if player_number == 1:
        game['player1_move'] = move
    else:
        game['player2_move'] = move
    
    print(f"[WEB] Room {room_id}: P1={game['player1_move']}, P2={game['player2_move']}")
    
    # Kiểm tra xem cả 2 players đã chọn nước đi chưa
    if game['player1_move'] and game['player2_move']:
        # Tính kết quả bằng game logic
        result1, result2 = determine_winner(game['player1_move'], game['player2_move'])
        
        print(f"[WEB] Results: P1={result1}, P2={result2}")
        
        # Lấy player names
        player1_info = players.get(game['player1_sid'], {})
        player2_info = players.get(game['player2_sid'], {})
        
        player1_name = player1_info.get('name', 'Player 1')
        player2_name = player2_info.get('name', 'Player 2')
        
        # Gửi kết quả về cho player 1
        emit('game_result', {
            'result': result1,
            'your_move': game['player1_move'],
            'opponent_move': game['player2_move'],
            'your_name': player1_name,
            'opponent_name': player2_name
        }, room=game['player1_sid'])
        
        # Gửi kết quả về cho player 2
        emit('game_result', {
            'result': result2,
            'your_move': game['player2_move'],
            'opponent_move': game['player1_move'],
            'your_name': player2_name,
            'opponent_name': player1_name
        }, room=game['player2_sid'])
        
        # Dọn dẹp game
        leave_room(room_id, sid=game['player1_sid'])
        leave_room(room_id, sid=game['player2_sid'])
        
        # Lưu last_room_id để có thể rematch, reset player_number
        if game['player1_sid'] in players:
            players[game['player1_sid']]['last_room_id'] = room_id
            players[game['player1_sid']]['room_id'] = None
            players[game['player1_sid']]['player_number'] = None
        
        if game['player2_sid'] in players:
            players[game['player2_sid']]['last_room_id'] = room_id
            players[game['player2_sid']]['room_id'] = None
            players[game['player2_sid']]['player_number'] = None
        
        # Xóa game
        del active_games[room_id]
        
        print(f"[WEB] Game {room_id} completed and cleaned up")


@socketio.on('request_rematch')
def handle_request_rematch(data):
    """
    Xử lý khi player request chơi lại với cùng đối thủ.
    Nếu cả 2 đồng ý → Bắt đầu game mới ngay.
    """
    sid = request.sid
    room_id = data.get('room_id')
    
    print(f"[WEB] Rematch request from {sid} for room {room_id}")
    
    if not room_id:
        return
    
    # Tạo rematch request nếu chưa có
    if room_id not in rematch_requests:
        # Tìm opponent có cùng last_room_id
        opponent_sid = None
        
        for other_sid, other_info in players.items():
            if other_sid != sid:
                # Check nếu cùng last_room_id
                if other_info.get('last_room_id') == room_id:
                    opponent_sid = other_sid
                    break
        
        if not opponent_sid:
            print(f"[WEB] No opponent found for rematch room {room_id}")
            emit('rematch_declined', {'message': 'Không tìm thấy đối thủ'})
            return
        
        print(f"[WEB] Creating rematch request for room {room_id}: {sid} vs {opponent_sid}")
        
        # Init rematch request
        rematch_requests[room_id] = {
            'player1_sid': sid,
            'player2_sid': opponent_sid,
            'player1_ready': False,
            'player2_ready': False
        }
    
    # Mark player ready
    rematch = rematch_requests[room_id]
    if sid == rematch['player1_sid']:
        rematch['player1_ready'] = True
    elif sid == rematch['player2_sid']:
        rematch['player2_ready'] = True
    
    print(f"[WEB] Rematch status for {room_id}: P1={rematch['player1_ready']}, P2={rematch['player2_ready']}")
    
    # Kiểm tra xem cả 2 đã ready chưa
    if rematch['player1_ready'] and rematch['player2_ready']:
        # Cả 2 đồng ý! Bắt đầu game mới
        print(f"[WEB] Rematch accepted for room {room_id}!")
        
        # Tạo game mới với cùng room_id
        active_games[room_id] = {
            'player1_sid': rematch['player1_sid'],
            'player2_sid': rematch['player2_sid'],
            'player1_move': None,
            'player2_move': None
        }
        
        # Join room lại
        join_room(room_id, sid=rematch['player1_sid'])
        join_room(room_id, sid=rematch['player2_sid'])
        
        # Update players dict với room_id và player_number
        if rematch['player1_sid'] in players:
            players[rematch['player1_sid']]['room_id'] = room_id
            players[rematch['player1_sid']]['player_number'] = 1
        
        if rematch['player2_sid'] in players:
            players[rematch['player2_sid']]['room_id'] = room_id
            players[rematch['player2_sid']]['player_number'] = 2
        
        # Notify cả 2 players
        emit('rematch_accepted', {'room_id': room_id}, room=rematch['player1_sid'])
        emit('rematch_accepted', {'room_id': room_id}, room=rematch['player2_sid'])
        
        # Clean up rematch request
        del rematch_requests[room_id]


@socketio.on('find_new_match')
def handle_find_new_match(data):
    """
    Xử lý khi player muốn tìm đối thủ mới thay vì rematch.
    Decline rematch request và notify opponent.
    """
    sid = request.sid
    room_id = data.get('room_id')
    
    print(f"[WEB] Player {sid} declined rematch for room {room_id}")
    
    if room_id and room_id in rematch_requests:
        rematch = rematch_requests[room_id]
        
        # Tìm opponent
        opponent_sid = None
        if sid == rematch['player1_sid']:
            opponent_sid = rematch['player2_sid']
        elif sid == rematch['player2_sid']:
            opponent_sid = rematch['player1_sid']
        
        # Notify opponent
        if opponent_sid:
            emit('rematch_declined', {
                'message': 'Đối thủ muốn tìm trận mới'
            }, room=opponent_sid)
        
        # Clean up
        del rematch_requests[room_id]


if __name__ == '__main__':
    print("=" * 60)
    print("🌐 Rock-Paper-Scissors Web Server")
    print("=" * 60)
    print("Server starting on http://localhost:5000")
    print("Open browser and navigate to http://localhost:5000")
    print("=" * 60)
    print()
    
    # Chạy server với debug mode
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
