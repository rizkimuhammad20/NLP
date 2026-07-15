<?php
header('Content-Type: application/json');

// Menerima input JSON dari script.js
$inputData = json_decode(file_get_contents('php://input'), true);
$userText = isset($inputData['text']) ? $inputData['text'] : '';

if (empty($userText)) {
    echo json_encode(['reply' => 'Maaf, teks ulasan tidak boleh kosong.']);
    exit;
}

// Menembak API Python Flask (app.py) di port 5000
$url = 'http://127.0.0.1:5000/predict';
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
$sentimen = $result['sentimen'];

// Berikan jawaban chatbot yang interaktif berdasarkan sentimen dari Python
if ($sentimen === 'positif') {
    $reply = "✨ **Analisis Sentimen: POSITIF**<br><br>Terima kasih atas ulasan positif Anda! Senang bisa memberikan layanan terbaik bagi perjalanan Anda bersama TransJakarta.";
} else {
    $reply = "⚠️ **Analisis Sentimen: NEGATIF**<br><br>Kami memohon maaf atas ketidaknyamanan Anda. Keluhan Anda mengenai sistem/layanan TiJe telah kami catat untuk bahan evaluasi tim operasional.";
}

echo json_encode(['reply' => $reply, 'sentimen' => $sentimen]);
?>