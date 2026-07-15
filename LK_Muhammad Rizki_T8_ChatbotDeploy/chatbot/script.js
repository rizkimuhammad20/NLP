document.getElementById('sendBtn').addEventListener('click', sendMessage);
document.getElementById('userInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') sendMessage();
});

function sendMessage() {
    const inputEl = document.getElementById('userInput');
    const messageText = inputEl.value.trim();
    
    if (messageText === '') return;
    
    const chatBox = document.getElementById('chatBox');
    
    // 1. Tampilkan pesan user ke layar chat
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.textContent = messageText;
    chatBox.appendChild(userDiv);
    
    // Kosongkan input dan scroll ke bawah
    inputEl.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;
    
    // 2. Tampilkan status "Sedang berpikir..." untuk bot sementara waktu
    const botLoadingDiv = document.createElement('div');
    botLoadingDiv.className = 'message bot-message';
    botLoadingDiv.innerText = 'Typing...';
    chatBox.appendChild(botLoadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    // 3. Kirim data ke chat.php menggunakan Fetch API
    fetch('index.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: messageText })
    })
    .then(response => response.json())
    .then(data => {
        // Hapus tulisan "Typing..." lalu ganti dengan jawaban riil dari model AI
        botLoadingDiv.innerHTML = data.reply;
        
        // Opsional: Berikan sedikit style border atau warna berdasarkan sentimen kembalian PHP
        if(data.sentimen === 'positif') {
            botLoadingDiv.style.borderLeft = '4px solid #4CAF50';
        } else if(data.sentimen === 'negatif') {
            botLoadingDiv.style.borderLeft = '4px solid #F44336';
        }
        
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        botLoadingDiv.innerText = '⚠️ Terjadi kesalahan koneksi jaringan.';
        console.error('Error:', error);
    });
}