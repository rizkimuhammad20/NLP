<?php
header('Content-Type: application/json');
// Mengizinkan CORS jika frontend diakses dari origin berbeda
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: Content-Type");

// Menerima input JSON dari script.js
$inputData = json_decode(file_get_contents('php://input'), true);
$userText = isset($inputData['text']) ? $inputData['text'] : '';

if (empty($userText)) {
    echo json_encode(['reply' => 'Maaf, teks ulasan tidak boleh kosong.']);
    exit;
}

// Menembak API Python Flask (app.py) di port 5000
$url = 'http://127.0.0.1:5001/predict';
$data = json_encode(['text' => $userText]);

$options = [
    'http' => [
        'header'  => "Content-type: application/json\r\n",
        'method'  => 'POST',
        'content' => $data,
    ],
];

$context  = stream_context_create($options);
$response = file_get_contents($url, false, $context);

if ($response === FALSE) {
    echo json_encode(['reply' => '⚠️ Gagal terhubung dengan server AI (app.py). Pastikan Flask sudah berjalan.']);
    exit;
}

$result = json_decode($response, true);

// --- PENYESUAIAN LOGIKA UNTUK MENANGKAP INTENT & SENTIMEN ---

// 1. Cek apakah yang dikembalikan adalah Intent Terstruktur (Bukan Ulasan Sentimen)
if (isset($result['tipe']) && $result['tipe'] === 'intent_response') {
    $reply = $result['respons'];
    $sentimen = 'intent'; // Kita tandai tipenya sebagai intent biasa
}
// 2. Jika tipenya adalah Analisis Sentimen (SVM)
else if (isset($result['tipe']) && $result['tipe'] === 'sentiment_analysis') {
    $sentimen = $result['sentimen'];

    if ($sentimen === 'positif') {
        $reply = "✨ <b>Analisis Sentimen: POSITIF</b><br><br>Terima kasih atas ulasan positif Anda! Senang bisa memberikan layanan terbaik bagi perjalanan Anda bersama TransJakarta.";
    } else {
        $reply = "⚠️ <b>Analisis Sentimen: NEGATIF</b><br><br>Kami memohon maaf atas ketidaknyamanan Anda. Keluhan Anda mengenai sistem/layanan TiJe telah kami catat untuk bahan evaluasi tim operasional.";
    }
}
// 3. Cadangan jika format JSON Python tidak sesuai ekspektasi
else {
    $reply = "Maaf, sistem gagal membaca format data dari server AI.";
    $sentimen = 'unknown';
}

// Kembalikan jawaban final ke script.js
echo json_encode([
    'reply' => $reply,
    'sentimen' => $sentimen
]);
