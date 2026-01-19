// Kết nối tới Socket.IO server
const socket = io();

// Lấy DOM elements
const nameInputSection = document.getElementById('name-input-section');
const nameInput = document.getElementById('name-input');
const enterGameBtn = document.getElementById('enter-game-btn');
const playerInfoSection = document.getElementById('player-info-section');
const playerAvatarEl = document.getElementById('player-avatar');
const playerNameEl = document.getElementById('player-name');
const opponentAvatarEl = document.getElementById('opponent-avatar');
const opponentNameEl = document.getElementById('opponent-name');
const opponentCard = document.querySelector('.opponent-card');

const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');
const connectBtn = document.getElementById('connect-btn');
const rematchSection = document.getElementById('rematch-section');
const rematchBtn = document.getElementById('rematch-btn');
const newMatchBtn = document.getElementById('new-match-btn');
const movesSection = document.getElementById('moves-section');
const moveBtns = document.querySelectorAll('.move-btn');

// Game state
let inGame = false;
let gameEnded = false;
let playerName = '';
let playerAvatar = '';
let currentRoomId = null;
let waitingForRematch = false;

// Avatar list - random emojis
const avatars = [
    '😀', '😃', '😄', '😁', '😆', '😊', '😎', '🤓', '🥳', '🤩',
    '😺', '😸', '😹', '😻', '🐶', '🐱', '🐭', '🐹', '🐰', '🦊',
    '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🙈'
];

// Random avatar function
function getRandomAvatar() {
    return avatars[Math.floor(Math.random() * avatars.length)];
}

// Enter game button handler
enterGameBtn.addEventListener('click', () => {
    const name = nameInput.value.trim();
    
    // Validate name
    if (!name || name.length < 2) {
        nameInput.style.borderColor = '#ef4444';
        nameInput.placeholder = 'Vui lòng nhập tên (ít nhất 2 ký tự)';
        return;
    }
    
    // Set player info
    playerName = name;
    playerAvatar = getRandomAvatar();
    
    // Update UI
    playerAvatarEl.textContent = playerAvatar;
    playerNameEl.textContent = playerName;
    
    // Hide name input, show player info
    nameInputSection.classList.add('hidden');
    playerInfoSection.classList.remove('hidden');
    connectBtn.classList.remove('hidden');
    
    // Connect to server với player info
    socket.emit('set_player_info', {
        name: playerName,
        avatar: playerAvatar
    });
    
    updateStatus('Đã sẵn sàng! Click Tìm trận để bắt đầu', 'success');
});

// Allow Enter key to submit name
nameInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        enterGameBtn.click();
    }
});

// Cập nhật status text và màu sắc
function updateStatus(text, type = '') {
    statusEl.textContent = text;
    statusEl.className = 'status-text';
    if (type) {
        statusEl.classList.add(type);
    }
}

// Hiển thị kết quả game
function showResult(text, type = '') {
    resultEl.textContent = text;
    resultEl.className = 'result-text';
    if (type) {
        resultEl.classList.add(type);
    }
}

// Ẩn result
function hideResult() {
    resultEl.textContent = '';
    resultEl.className = 'result-text';
}

// Hiện các nút chọn move
function showMoveButtons() {
    movesSection.classList.remove('hidden');
    enableMoveButtons();
}

// Ẩn các nút move
function hideMoveButtons() {
    movesSection.classList.add('hidden');
}

// Enable tất cả nút move
function enableMoveButtons() {
    moveBtns.forEach(btn => {
        btn.disabled = false;
    });
}

// Disable tất cả nút move
function disableMoveButtons() {
    moveBtns.forEach(btn => {
        btn.disabled = true;
    });
}

// Reset UI về trạng thái ban đầu
function resetUI() {
    updateStatus('Đã sẵn sàng! Click Tìm trận', 'success');
    hideResult();
    hideMoveButtons();
    connectBtn.disabled = false;
    connectBtn.textContent = '🔌 Tìm trận';
    connectBtn.classList.remove('hidden');
    
    // Hide rematch buttons
    rematchSection.classList.add('hidden');
    
    // Reset opponent
    opponentAvatarEl.textContent = '❓';
    opponentNameEl.textContent = 'Đang tìm...';
    opponentCard.classList.remove('matched');
    
    inGame = false;
    gameEnded = false;
    currentRoomId = null;
    waitingForRematch = false;
}

// Event: Click nút "Tìm trận"
connectBtn.addEventListener('click', () => {
    console.log('[CLIENT] Finding match...');
    connectBtn.disabled = true;
    connectBtn.classList.add('hidden');
    rematchSection.classList.add('hidden');
    socket.emit('find_match');
    updateStatus('Đang tìm đối thủ...', 'waiting');
    
    // Reset opponent display
    opponentAvatarEl.textContent = '❓';
    opponentNameEl.textContent = 'Đang tìm...';
    opponentCard.classList.remove('matched');
});

// Event: Click nút "Chơi tiếp" (rematch)
rematchBtn.addEventListener('click', () => {
    console.log('[CLIENT] Requesting rematch...');
    rematchBtn.disabled = true;
    newMatchBtn.disabled = true;
    waitingForRematch = true;
    socket.emit('request_rematch', { room_id: currentRoomId });
    updateStatus(`Chờ ${opponentNameEl.textContent} quyết định...`, 'waiting');
});

// Event: Click nút "Tìm trận mới"
newMatchBtn.addEventListener('click', () => {
    console.log('[CLIENT] Finding new match...');
    socket.emit('find_new_match', { room_id: currentRoomId });
    resetUI();
    connectBtn.click();
});

// Event: Click các nút move (Búa/Bao/Kéo)
moveBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const move = btn.dataset.move;
        console.log(`[CLIENT] Selected move: ${move}`);
        
        socket.emit('send_move', { move: move });
        disableMoveButtons();
        
        const moveNames = {
            'ROCK': '✊ Búa',
            'PAPER': '✋ Bao',
            'SCISSORS': '✌️ Kéo'
        };
        updateStatus(`Đã chọn ${moveNames[move]}, chờ ${opponentNameEl.textContent}...`, 'info');
    });
});

// Socket event: Kết nối thành công tới server
socket.on('connect', () => {
    console.log('[CLIENT] Connected to server');
});

// Socket event: Mất kết nối với server
socket.on('disconnect', () => {
    console.log('[CLIENT] Disconnected from server');
    if (!gameEnded) {
        updateStatus('Mất kết nối với server', 'error');
        resetUI();
    }
});

// Socket event: Đang chờ đối thủ
socket.on('waiting', () => {
    console.log('[CLIENT] Waiting for opponent...');
    updateStatus('Đang chờ đối thủ...', 'waiting');
    statusEl.classList.add('pulse');
});

// Socket event: Tìm thấy trận đấu
socket.on('match_found', (data) => {
    console.log('[CLIENT] Match found!', data);
    statusEl.classList.remove('pulse');
    
    // Lưu room ID
    currentRoomId = data.room_id;
    
    // Hiển thị thông tin đối thủ
    if (data.opponent_name && data.opponent_avatar) {
        opponentAvatarEl.textContent = data.opponent_avatar;
        opponentNameEl.textContent = data.opponent_name;
        opponentCard.classList.add('matched');
        
        updateStatus(`Tìm thấy! Đối thủ: ${data.opponent_name} ${data.opponent_avatar}`, 'success');
    } else {
        updateStatus('Tìm thấy đối thủ! Chọn nước đi', 'success');
    }
    
    hideResult();
    rematchSection.classList.add('hidden');
    showMoveButtons();
    inGame = true;
});

// Socket event: Nhận kết quả game
socket.on('game_result', (data) => {
    console.log('[CLIENT] Game result:', data);
    gameEnded = true;
    
    const { result, your_move, opponent_move, your_name, opponent_name } = data;
    
    const moveNames = {
        'ROCK': '✊ Búa',
        'PAPER': '✋ Bao',
        'SCISSORS': '✌️ Kéo'
    };
    
    // Hiển thị kết quả
    if (result === 'WIN') {
        showResult(`🎉 ${your_name || playerName} THẮNG! 🎉`, 'win');
    } else if (result === 'LOSE') {
        showResult(`😢 ${opponent_name || 'Đối thủ'} THẮNG! 😢`, 'lose');
    } else if (result === 'DRAW') {
        showResult('🤝 HÒA! 🤝', 'draw');
    }
    
    // Hiển thị chi tiết moves
    const yourMoveText = `${your_name || playerName}: ${moveNames[your_move]}`;
    const opponentMoveText = `${opponent_name || 'Đối thủ'}: ${moveNames[opponent_move]}`;
    updateStatus(`${yourMoveText} vs ${opponentMoveText}`, 'info');
    
    hideMoveButtons();
    
    // Sau 2 giây, hiện rematch buttons
    setTimeout(() => {
        connectBtn.classList.add('hidden');
        rematchSection.classList.remove('hidden');
        rematchBtn.disabled = false;
        newMatchBtn.disabled = false;
        updateStatus('Chọn: Chơi tiếp hoặc Tìm trận mới', 'success');
        inGame = false;
        gameEnded = false;
    }, 2000);
});

// Socket event: Rematch được chấp nhận
socket.on('rematch_accepted', (data) => {
    console.log('[CLIENT] Rematch accepted!', data);
    waitingForRematch = false;
    
    // Reset UI để game mới
    hideResult();
    rematchSection.classList.add('hidden');
    updateStatus(`Rematch! Chọn nước đi`, 'success');
    showMoveButtons();
    inGame = true;
});

// Socket event: Rematch bị từ chối hoặc timeout
socket.on('rematch_declined', (data) => {
    console.log('[CLIENT] Rematch declined:', data);
    waitingForRematch = false;
    updateStatus(data.message || 'Đối thủ không muốn chơi tiếp', 'error');
    
    // Show tìm trận mới
    setTimeout(() => {
        resetUI();
    }, 2000);
});

// Socket event: Đối thủ disconnect
socket.on('opponent_disconnected', () => {
    console.log('[CLIENT] Opponent disconnected');
    updateStatus(`${opponentNameEl.textContent} đã thoát`, 'error');
    showResult('❌ Đối thủ ngắt kết nối', 'error');
    hideMoveButtons();
    
    setTimeout(() => {
        resetUI();
    }, 3000);
});

// Socket event: Lỗi
socket.on('error', (data) => {
    console.error('[CLIENT] Error:', data);
    showResult(`❌ Lỗi: ${data.message}`, 'error');
    updateStatus('Có lỗi xảy ra', 'error');
});

// Khởi tạo khi load page
console.log('[CLIENT] Game initialized');
