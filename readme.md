# Aplikasi Chat PDF 

Aplikasi chat PDF canggih yang memungkinkan pengguna berinteraksi dengan dokumen mereka menggunakan Large Language Model lokal melalui LM Studio. Fitur mencakup autentikasi pengguna, riwayat chat persisten, manajemen dokumen, dan kemampuan menjawab pertanyaan yang cerdas.

## ✨ Fitur Utama

### Fungsionalitas Inti
- 🔐 **Sistem Autentikasi Pengguna** - Login/registrasi aman dengan database SQLite
- 📚 **Pemrosesan Multi-PDF** - Upload dan proses beberapa dokumen PDF sekaligus
- 💬 **Interface Chat Cerdas** - Ajukan pertanyaan tentang dokumen Anda dan dapatkan jawaban kontekstual
- 🧠 **Integrasi LLM Lokal** - Menggunakan LM Studio untuk respons AI yang berfokus pada privasi dan offline
- 📖 **Rangkuman Dokumen** - Buat rangkuman cepat dari dokumen yang diupload
- 🔍 **Kutipan Sumber** - Lihat persis dari halaman dan dokumen mana informasi berasal

### Manajemen Data
- 💾 **Riwayat Chat Persisten** - Semua percakapan disimpan dan dipulihkan antar sesi
- 📄 **Riwayat Dokumen** - Lacak semua dokumen yang diupload dengan timestamp
- 🏪 **Caching Vector Store** - Proses dokumen sekali, gunakan embedding untuk respons lebih cepat
- 🗃️ **Data Spesifik Pengguna** - Setiap pengguna memiliki dokumen dan riwayat chat sendiri

### Kustomisasi
- ⚙️ **Parameter yang Dapat Disesuaikan** - Fine-tune temperature, max tokens, chunk size, dan pengaturan retrieval
- 🔧 **Pemilihan Model** - Pilih dari model yang tersedia di instance LM Studio Anda
- 📊 **Pengaturan Dokumen Lanjutan** - Konfigurasi parameter chunking dan similarity search

## 🚀 Panduan Cepat

### Prasyarat

1. **Python 3.8+** terinstal di sistem Anda
2. **LM Studio** terinstal dan berjalan dengan model yang dimuat
3. **Git** untuk cloning repository

### Instalasi

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd enhanced-pdf-chat
   ```

2. **Buat virtual environment**
   ```bash
   python -m venv venv
   
   # Di Windows
   venv\Scripts\activate
   
   # Di macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit file .env dengan konfigurasi Anda (jika diperlukan)
   ```

5. **Jalankan aplikasi**
   ```bash
   streamlit run main.py
   ```

## 📋 Kebutuhan Sistem

Buat file `requirements.txt` dengan dependencies berikut:

```txt
streamlit>=1.28.0
PyPDF2>=3.0.1
langchain>=0.0.350
langchain-community>=0.0.10
faiss-cpu>=1.7.4
sentence-transformers>=2.2.2
openai>=1.3.0
python-dotenv>=1.0.0
requests>=2.31.0
```

## 🔧 Konfigurasi

### Environment Variables (.env)

Buat file `.env` di direktori root:

```env
# Konfigurasi LM Studio
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_TIMEOUT=30

# Konfigurasi Database
DATABASE_PATH=pdf_chat.db

# Konfigurasi Vector Store
VECTOR_STORE_PATH=vectorstore

# Pengaturan Aplikasi
DEBUG=False
```

### Setup LM Studio

1. **Download dan install LM Studio** dari [lmstudio.ai](https://lmstudio.ai/)
2. **Download model** (disarankan: Llama 2, Mistral, atau sejenisnya)
3. **Load model** di LM Studio
4. **Start local server** (biasanya berjalan di `http://127.0.0.1:1234`)

## 📖 Panduan Penggunaan

### Memulai

1. **Jalankan aplikasi**
   ```bash
   streamlit run main.py
   ```

2. **Buat akun** atau **login** dengan kredensial yang ada

3. **Upload dokumen PDF** menggunakan file uploader di sidebar

4. **Proses PDF Anda** dengan mengklik tombol "Process PDFs"

5. **Hubungkan ke LM Studio** dan pilih model yang Anda inginkan

6. **Mulai chat** dengan dokumen Anda!

### Panduan Fitur Utama

#### Pemrosesan Dokumen
- Upload beberapa PDF secara bersamaan
- Dokumen otomatis di-chunk dan di-embed
- Vector store di-cache untuk akses selanjutnya yang lebih cepat
- Lihat riwayat upload dokumen Anda

#### Interface Chat
- Ajukan pertanyaan dalam bahasa alami
- Terima jawaban kontekstual dengan kutipan sumber
- Lihat dari halaman dan dokumen mana informasi berasal
- Riwayat chat otomatis disimpan dan dipulihkan

#### Manajemen Model
- Hubungkan ke instance LM Studio lokal Anda
- Pilih dari model yang tersedia dan dimuat
- Sesuaikan temperature dan batas token
- Fine-tune parameter chunking dokumen

## 🏗️ Struktur Proyek

```
enhanced-pdf-chat/
├── main.py                 # Entry point aplikasi utama
├── src/
│   ├── auth.py            # Manajemen autentikasi
│   ├── database.py        # Operasi database dan model
│   ├── lm_studio.py       # Integrasi API LM Studio
│   ├── models.py          # Model data dan state aplikasi
│   ├── pdf_processor.py   # Pemrosesan PDF dan vektorisasi
│   └── ui_components.py   # Komponen UI Streamlit
├── vectorstore/           # Embedding vektor yang di-cache (dibuat otomatis)
├── pdf_chat.db           # Database SQLite (dibuat otomatis)
├── requirements.txt       # Dependencies Python
├── .env                   # Konfigurasi environment
└── README.md             # File ini
```

## 🗄️ Skema Database

Aplikasi menggunakan SQLite dengan tabel berikut:

- **users** - Akun pengguna dan autentikasi
- **documents** - Metadata dokumen dan hash file
- **chat_history** - Riwayat percakapan per pengguna
- **user_sessions** - Manajemen sesi (penggunaan masa depan)

## 🔧 Konfigurasi Lanjutan

### Parameter Pemrosesan Dokumen

- **Chunk Size**: Ukuran chunk teks (default: 2500 karakter)
- **Chunk Overlap**: Overlap antar chunk (default: 500 karakter)
- **Similarity K**: Jumlah chunk serupa yang diambil (default: 5)

### Parameter Model

- **Temperature**: Mengontrol keacakan respons (0.0-1.0)
- **Max Tokens**: Panjang respons maksimum (100-4000)

### Pengaturan Vector Store

- Menggunakan **sentence-transformers/all-MiniLM-L6-v2** untuk embedding
- **FAISS** untuk pencarian similarity yang efisien
- Caching otomatis berdasarkan hash dokumen

## 🐛 Pemecahan Masalah

### Masalah Umum

**"Connection refused - Is LM Studio running?"**
- Pastikan LM Studio berjalan dan model dimuat
- Periksa bahwa server dapat diakses di `http://127.0.0.1:1234`
- Verifikasi tidak ada firewall yang memblokir koneksi

**"No models available"**
- Load model di LM Studio
- Klik "Refresh Models" di sidebar
- Pastikan model dimuat dengan benar dan tidak hanya didownload

**"Error creating vectorstore"**
- Periksa apakah PDF Anda berbasis teks (bukan gambar scan)
- Pastikan ruang disk yang cukup untuk embedding
- Coba kurangi chunk size jika memproses dokumen besar

**Error database**
- Pastikan write permission di direktori aplikasi
- Hapus `pdf_chat.db` untuk reset database jika corrupt

### Tips Performa

- Proses dokumen dengan konten serupa bersamaan untuk konteks yang lebih baik
- Gunakan chunk size yang sesuai (lebih besar untuk dokumen teknis, lebih kecil untuk teks umum)
- Sesuaikan similarity K berdasarkan panjang dokumen dan kompleksitas pertanyaan
- Pertimbangkan menggunakan model yang lebih powerful untuk query kompleks

## 🤝 Kontribusi

1. Fork repository
2. Buat feature branch (`git checkout -b feature/fitur-menakjubkan`)
3. Commit perubahan Anda (`git commit -m 'Tambah fitur menakjubkan'`)
4. Push ke branch (`git push origin feature/fitur-menakjubkan`)
5. Buka Pull Request

## 📄 Lisensi

Proyek ini dilisensikan di bawah MIT License - lihat file [LICENSE](LICENSE) untuk detail.

## 🙏 Ucapan Terima Kasih

- **Streamlit** untuk framework web app yang luar biasa
- **LangChain** untuk pemrosesan dokumen dan operasi vektor
- **LM Studio** untuk kemampuan hosting LLM lokal
- **Sentence Transformers** untuk generasi embedding
- **FAISS** untuk pencarian similarity yang efisien

## 📞 Dukungan

Jika Anda mengalami masalah atau memiliki pertanyaan:

1. Periksa bagian pemecahan masalah di atas
2. Tinjau halaman [Issues](../../issues)
3. Buat issue baru dengan informasi detail tentang masalah Anda

---

**Selamat ber-chat dengan PDF Anda! 📚🤖**
