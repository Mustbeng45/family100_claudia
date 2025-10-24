# Famili 100 – Ulang Tahun Claudia (Streamlit)

## Menjalankan di VS Code (Windows/Mac/Linux)
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## Pemakaian
- Pertanyaan default sudah terisi dari `questions_claudia.json`
- Ubah nama tim di sidebar
- Ungkap (reveal) jawaban sesuai permainan
- Berikan poin putaran ke tim pemenang
- Gunakan "Strike +1/-1" jika ingin gaya Family 100
- Timer manual bisa dikurangi per detik

## Format JSON kustom
```json
[
  {
    "question": "Contoh pertanyaan",
    "answers": [
      {"text": "Jawaban A", "points": 30},
      {"text": "Jawaban B", "points": 20}
    ]
  }
]
```

## Catatan deploy ke PythonAnywhere (ringkas)
1. Upload semua file (app.py, questions_claudia.json, requirements.txt)
2. Buat virtualenv dan install requirements
3. Jalankan `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0` melalui Always-on task atau konfigurasi app (detail lengkap bisa saya siapkan nanti)
```
