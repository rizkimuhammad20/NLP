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
    
    // 2. Tampilkan status "Typing..." untuk bot sementara waktu
    const botLoadingDiv = document.createElement('div');
    botLoadingDiv.className = 'message bot-message';
    botLoadingDiv.innerText = 'Typing...';
    chatBox.appendChild(botLoadingDiv);
    chatBox.scrollTop = chatBox.scrollHeight;

    // 3. Kirim data ke Flask backend menggunakan Fetch API
    fetch('/predict', { 
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: messageText })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Jika ada error dari sisi Python/Server
        if (data.status === 'error') {
            botLoadingDiv.innerHTML = "Error: " + data.message;
            return;
        }

        // A. JIKA MERESPONS PERCAKAPAN BIASA (INTENT/KEYWORD CHAT)
        if (data.tipe === 'intent_response') {
            botLoadingDiv.innerHTML = data.respons; 
            
        // B. JIKA MERESPONS HASIL ANALISIS SENTIMEN (MODEL SVM & LOGIKA HYBRID)
        } else if (data.tipe === 'sentiment_analysis') {
            // Menampilkan hasil label sentimen beserta kalimat respons evaluasi resmi
            botLoadingDiv.innerHTML = "Hasil analisis sentimen: <b style='text-transform: capitalize;'>" + data.sentimen + "</b><br><br>" + data.pesan;
            
            // Memberikan style warna indikator garis kiri (border-left) sesuai dengan hasil 3 sentimen
            if(data.sentimen === 'positif') {
                botLoadingDiv.style.borderLeft = '4px solid #4CAF50'; // Hijau untuk Kepuasan
            } else if(data.sentimen === 'negatif') {
                botLoadingDiv.style.borderLeft = '4px solid #F44336'; // Merah untuk Keluhan/Kritik Tajam
            } else if(data.sentimen === 'netral') {
                botLoadingDiv.style.borderLeft = '4px solid #2196F3'; // Biru untuk Netral / Ulasan Campuran
            }
        }
        
        // Scroll otomatis ke pesan paling bawah
        chatBox.scrollTop = chatBox.scrollHeight;
    })
    .catch(error => {
        // Tampilkan pesan error jika koneksi ke server Flask terputus
        botLoadingDiv.innerText = '⚠️ Terjadi kesalahan koneksi jaringan.';
        console.error('Error:', error);
    });
}