from flask import Flask, request, jsonify, render_template  
import pickle
import sys
import re  

try:
    import joblib
except Exception:
    joblib = None

app = Flask(__name__)

def _robust_load(path):
    """Coba beberapa cara untuk memuat file model/objek pickle."""
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as err1:
        try:
            with open(path, 'rb') as f:
                return pickle.load(f, encoding='latin1')
        except Exception:
            if joblib is not None:
                try:
                    return joblib.load(path)
                except Exception:
                    pass
        raise err1

# Load model dan TF-IDF yang sudah kamu simpan sebelumnya
model_path = 'svm_sentiment.pkl'
tfidf_path = 'tfidf_vectorizer.pkl'

try:
    model_svm = _robust_load(model_path)
except Exception as e:
    print(f"Gagal memuat model dari {model_path}: {e}", file=sys.stderr)
    raise

try:
    tfidf = _robust_load(tfidf_path)
except Exception as e:
    print(f"Gagal memuat tfidf dari {tfidf_path}: {e}", file=sys.stderr)
    raise

# --- DEFINISI INTENT DAN RESPONS ---
INTENT_RESPONSES = {
    "salam": {
        "keywords": [r"\bhalo\b", r"\bhai\b", r"\bassalamualaikum\b", r"\bhi\b", r"\bselamat pagi\b", r"\bselamat siang\b", r"\bselamat sore\b", r"\bselamat malam\b", r"\bapa kabar\b", r"\bp\b"],
        "reply": "Halo! Ada yang bisa saya bantu hari ini?"
    },
    "tanya_kabar": {
        "keywords": [r"apa kabar", r"bagaimana kabar", r"gimana kabar"],
        "reply": "Saya adalah sistem AI, kabar saya selalu baik dan siap membantu Anda!"
    },
    "terima_kasih": {
        "keywords": [r"terima kasih", r"makasih", r"thanks", r"suwun"],
        "reply": "Sama-sama! Senang bisa membantu Anda."
    },
    "perpisahan": {
        "keywords": [r"dadah", r"sampai jumpa", r"bye", r"selamat tinggal"],
        "reply": "Sampai jumpa lagi! Semoga hari Anda menyenangkan."
    },
    "identitas_bot": {
        "keywords": [r"siapa kamu", r"nama kamu", r"kamu siapa"],
        "reply": "Saya adalah Bot Analisis Sentimen yang siap mendeteksi emosi dari teks Anda."
    },
    "cara_kerja": {
        "keywords": [r"cara kerja", r"gimana caranya", r"cara pakai"],
        "reply": "Kirimkan teks atau ulasan Anda ke sini, dan saya akan menganalisis apakah maknanya positif atau negatif."
    },
    "fitur_bot": {
        "keywords": [r"bisa apa aja", r"fitur bot", r"menu bot"],
        "reply": "Saya bisa mendeteksi 8 intent percakapan dasar serta menganalisis sentimen positif/negatif menggunakan model SVM."
    },
    "pujian": {
        "keywords": [r"bot hebat", r"kamu pintar", r"kamu keren", r"botnya bagus", r"ai pintar"],
        "reply": "Terima kasih banyak atas pujiannya! Ini semua berkat developer saya."
    }
}

def cetak_intent(text):
    """Fungsi helper untuk mencocokkan teks dengan daftar intent."""
    text_lower = text.lower()
    for intent, data in INTENT_RESPONSES.items():
        for keyword in data["keywords"]:
            if re.search(keyword, text_lower):
                return intent, data["reply"]
    return None, None

# --- ROUTE FLASK ---

@app.route('/')
def home():
    # Mengembalikan file HTML UI Chatbot
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    user_text = data.get('text', '')
    
    if not user_text:
        return jsonify({'status': 'error', 'message': 'Teks kosong'}), 400
        
    # 1. Cek Intent Terlebih Dahulu
    intent_terdeteksi, respons_bot = cetak_intent(user_text)
    
    if intent_terdeteksi:
        return jsonify({
            'status': 'success',
            'tipe': 'intent_response',
            'intent': intent_terdeteksi,
            'respons': respons_bot
        })
        
    text_lower = user_text.lower()
    
    # 2. FILTER AMAN: DETEKSI HINAAN/MAKIAN SECARA LANGSUNG
    # Jika kalimat mengandung kata kasar murni, langsung paksa masuk NEGATIF tanpa toleransi filter lainnya
    kata_makian = [r'\bbego\b', r'\bjelek\b', r'\banjing\b', r'\bbangsat\b', r'\bburuk\b', r'\btolol\b',
                   r'\bkecewa\b', r'\bbodoh\b', r'\bgk berguna\b', r'\bcacat\b', r'\bmati\b', r'\bhapus\b',
                   r'\blelet\b', r'\btai\b', r'\bkocak\b']
    if any(re.search(pattern, text_lower) for pattern in kata_makian):
        return jsonify({
            'status': 'success',
            'tipe': 'sentiment_analysis',
            'sentimen': 'negatif',
            'pesan': "Mohon maaf jika pengalaman Anda kurang menyenangkan. Ulasan ini akan menjadi bahan evaluasi kami ke depannya."
        })

    # 3. DETEKSI ULASAN CAMPURAN (Pujian + Kritik) MENGGUNAKAN REGEX KATA UTUH (\b)
    # Filter \b memastikan kata murni "oke" tidak salah terpicu oleh kata "boong"
    kata_pujian = [r'\bkeren\b', r'\bbagus\b', r'\bmantap\b', r'\boke\b', r'\bhebat\b', r'\bsuka\b',
                   r'\bterima kasih\b', r'\bmakasih\b', r'\bcanggih\b', r'\bmembantu\b', r'\bbantu\b']
    kata_kritik = [r'\berror\b', r'\btapi\b', r'\bnamun\b', r'\bkurang\b', r'\blambat\b', r'\blemot\b', r'\bbug\b', r'\bperbaiki\b', r'\bhancur\b', r'\bngebug\b']
    
    ada_pujian = any(re.search(pattern, text_lower) for pattern in kata_pujian)
    ada_kritik = any(re.search(pattern, text_lower) for pattern in kata_kritik)
    
    if ada_pujian and ada_kritik:
        return jsonify({
            'status': 'success',
            'tipe': 'sentiment_analysis',
            'sentimen': 'netral', # Menggunakan kategori netral agar JS memunculkan border biru
            'pesan': "Terima kasih atas tanggapan positif Anda! Kami sangat senang mendengarnya. Dan ulasan ini akan menjadi bahan evaluasi kami ke depannya."
        })

    # 4. JALANKAN PREDIKSI NORMAL MENGGUNAKAN MODEL SVM (3-Kelas Asli)
    try:
        text_tfidf = tfidf.transform([user_text])
        raw_prediction = model_svm.predict(text_tfidf)
        
        if hasattr(raw_prediction, "__len__") and len(raw_prediction) > 0:
            prediction = raw_prediction[0]
        else:
            prediction = raw_prediction
            
        pred_str = str(prediction).strip().lower()
        
        if pred_str == 'positif':
            sentimen = "positif"
            pesan = "Terima kasih atas tanggapan positif Anda! Kami sangat senang mendengarnya."
            
        elif pred_str == 'netral':
            sentimen = "netral"
            pesan = "Tanggapan Anda bernada netral. Terima kasih atas ulasan dan masukan yang Anda berikan."
            
        else:  # 'negatif'
            sentimen = "negatif"
            pesan = "Mohon maaf jika pengalaman Anda kurang menyenangkan. Ulasan ini akan menjadi bahan evaluasi kami ke depannya."
        
        return jsonify({
            'status': 'success',
            'tipe': 'sentiment_analysis',
            'sentimen': sentimen,
            'pesan': pesan
        })

    except Exception as e:
        print(f"Error pada pemrosesan model SVM: {e}", file=sys.stderr)
        return jsonify({'status': 'error', 'message': f'Gagal memproses model: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)