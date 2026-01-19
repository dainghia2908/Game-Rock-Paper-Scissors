"""
Game Protocol for Rock-Paper-Scissors Multiplayer

File này chứa constants và helper functions dùng chung giữa server và client.
"""

# Network configuration
HOST = 'localhost'  # Server host
PORT = 9999  # Server port (không dùng cho web version)
BUFFER_SIZE = 1024  # Buffer size cho socket operations

# Timeout settings
SOCKET_TIMEOUT = 30  # Socket timeout (seconds)
MOVE_TIMEOUT = 60  # Timeout chờ player gửi move

# Server → Client messages
MSG_WAITING = "WAITING"  # Đang chờ đối thủ
MSG_START = "START"  # Game bắt đầu
MSG_OPPONENT_FOUND = "OPPONENT_FOUND"  # Tìm thấy đối thủ

# Result messages
MSG_WIN = "RESULT:WIN"  # Thắng
MSG_LOSE = "RESULT:LOSE"  # Thua
MSG_DRAW = "RESULT:DRAW"  # Hòa

# Error messages
MSG_ERROR = "ERROR"  # Lỗi chung
MSG_TIMEOUT = "ERROR:TIMEOUT"  # Player timeout
MSG_INVALID_MOVE = "ERROR:INVALID"  # Nước đi không hợp lệ
MSG_DISCONNECT = "ERROR:DISCONNECT"  # Đối thủ disconnect

# Move message format
MOVE_PREFIX = "MOVE:"  # Prefix cho move messages (VD: "MOVE:ROCK")

# Move types
MOVE_ROCK = "ROCK"  # Búa ✊
MOVE_PAPER = "PAPER"  # Bao ✋
MOVE_SCISSORS = "SCISSORS"  # Kéo ✌️

# Danh sách moves hợp lệ
VALID_MOVES = [MOVE_ROCK, MOVE_PAPER, MOVE_SCISSORS]

# Game rules - Luật chơi Oẳn Tù Tì
# Key: (move1, move2) → Value: result for player 1
GAME_RULES = {
    # Búa vs ...
    (MOVE_ROCK, MOVE_ROCK): "DRAW",  # Búa vs Búa → Hòa
    (MOVE_ROCK, MOVE_PAPER): "LOSE",  # Búa vs Bao → Thua
    (MOVE_ROCK, MOVE_SCISSORS): "WIN",  # Búa vs Kéo → Thắng
    
    # Bao vs ...
    (MOVE_PAPER, MOVE_ROCK): "WIN",  # Bao vs Búa → Thắng
    (MOVE_PAPER, MOVE_PAPER): "DRAW",  # Bao vs Bao → Hòa
    (MOVE_PAPER, MOVE_SCISSORS): "LOSE",  # Bao vs Kéo → Thua
    
    # Kéo vs ...
    (MOVE_SCISSORS, MOVE_ROCK): "LOSE",  # Kéo vs Búa → Thua
    (MOVE_SCISSORS, MOVE_PAPER): "WIN",  # Kéo vs Bao → Thắng
    (MOVE_SCISSORS, MOVE_SCISSORS): "DRAW",  # Kéo vs Kéo → Hòa
}

# Display names cho UI
MOVE_DISPLAY = {
    MOVE_ROCK: "✊ Búa",
    MOVE_PAPER: "✋ Bao",
    MOVE_SCISSORS: "✌️ Kéo",
}


def create_move_message(move):
    """
    Tạo message để gửi move.
    
    Args:
        move: ROCK, PAPER, hoặc SCISSORS
        
    Returns:
        str: Message format "MOVE:XXX"
        
    Raises:
        ValueError: Nếu move không hợp lệ
    """
    if move not in VALID_MOVES:
        raise ValueError(f"Invalid move: {move}")
    return f"{MOVE_PREFIX}{move}"


def parse_move_message(message):
    """
    Parse move message từ string.
    
    Args:
        message: String format "MOVE:XXX"
        
    Returns:
        str: Move type (ROCK/PAPER/SCISSORS) hoặc None nếu invalid
    """
    if not message.startswith(MOVE_PREFIX):
        return None
    move = message[len(MOVE_PREFIX):]
    return move if move in VALID_MOVES else None


def determine_winner(move1, move2):
    """
    Xác định người thắng dựa trên 2 moves.
    
    Args:
        move1: Move của player 1
        move2: Move của player 2
        
    Returns:
        tuple: (result_player1, result_player2)
               Mỗi result là "WIN", "LOSE", hoặc "DRAW"
               
    Example:
        >>> determine_winner("ROCK", "SCISSORS")
        ('WIN', 'LOSE')
    """
    result1 = GAME_RULES.get((move1, move2))
    
    # Tính result cho player 2 dựa trên result của player 1
    if result1 == "WIN":
        result2 = "LOSE"
    elif result1 == "LOSE":
        result2 = "WIN"
    else:  # DRAW
        result2 = "DRAW"
        
    return (result1, result2)


def format_result_message(result):
    """
    Format kết quả thành message.
    
    Args:
        result: "WIN", "LOSE", hoặc "DRAW"
        
    Returns:
        str: Format "RESULT:XXX"
    """
    return f"RESULT:{result}"


def is_valid_move(move):
    """Kiểm tra move có hợp lệ không"""
    return move in VALID_MOVES


def is_result_message(message):
    """Kiểm tra có phải result message không"""
    return message in [MSG_WIN, MSG_LOSE, MSG_DRAW]


def is_error_message(message):
    """Kiểm tra có phải error message không"""
    return message.startswith("ERROR")


# Testing code
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Game Protocol Module")
    print("=" * 60)
    
    print("\n[TEST] create_move_message:")
    print(f"  ROCK → {create_move_message(MOVE_ROCK)}")
    print(f"  PAPER → {create_move_message(MOVE_PAPER)}")
    print(f"  SCISSORS → {create_move_message(MOVE_SCISSORS)}")
    
    print("\n[TEST] parse_move_message:")
    print(f"  'MOVE:ROCK' → {parse_move_message('MOVE:ROCK')}")
    print(f"  'MOVE:PAPER' → {parse_move_message('MOVE:PAPER')}")
    print(f"  'INVALID' → {parse_move_message('INVALID')}")
    
    print("\n[TEST] determine_winner:")
    print(f"  ROCK vs SCISSORS → {determine_winner(MOVE_ROCK, MOVE_SCISSORS)}")
    print(f"  PAPER vs ROCK → {determine_winner(MOVE_PAPER, MOVE_ROCK)}")
    print(f"  SCISSORS vs PAPER → {determine_winner(MOVE_SCISSORS, MOVE_PAPER)}")
    print(f"  ROCK vs ROCK → {determine_winner(MOVE_ROCK, MOVE_ROCK)}")
    
    print("\n[TEST] Validation:")
    print(f"  is_valid_move('ROCK') → {is_valid_move(MOVE_ROCK)}")
    print(f"  is_valid_move('INVALID') → {is_valid_move('INVALID')}")
    print(f"  is_result_message('RESULT:WIN') → {is_result_message(MSG_WIN)}")
    print(f"  is_error_message('ERROR:TIMEOUT') → {is_error_message(MSG_TIMEOUT)}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
