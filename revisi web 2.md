# SISTEM PENJUALAN DAN INVENTORI
## Metode Waterfall - Untuk Tugas Akhir/Sidang

### Deskripsi
Sistem informasi manajemen inventori dan penjualan berbasis web yang dibangun menggunakan metode waterfall. Sistem ini mencakup fitur-fitur lengkap untuk mengelola data barang, stok, transaksi penjualan, dan laporan.

---

## FITUR SISTEM

| No | Fitur | Deskripsi |
|----|-------|------------|
| 1 | **Login Admin** | Sistem autentikasi dengan username dan password |
| 2 | **Data Barang** | CRUD data barang (kode, nama, kategori, harga) |
| 3 | **Stok Barang** | Monitoring dan penambahan stok barang |
| 4 | **Transaksi Penjualan** | Proses penjualan dengan mengurangi stok otomatis |
| 5 | **Laporan Penjualan** | Laporan transaksi dengan filter tanggal |
| 6 | **Notifikasi Stok** | Alert otomatis untuk stok habis dan menipis |

---

## TEKNOLOGI YANG DIGUNAKAN

- **Backend**: Python (Flask)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Metode**: Waterfall

---

## CARA MENJALANKAN

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
python app.py
```

### 3. Buka Browser
Buka URL: `http://localhost:5000`

---

## AKUN DEFAULT

| Field | Value |
|-------|-------|
| Username | `natadi11` |
| Password | `natadi11` |

---

## LINK AKSES

- `http://localhost:5000`
- `http://rumah-batik-lili.com:5000` (opsional, butuh entry hosts lokal)

> Jika Anda ingin menggunakan `https://rumah-batik-lili.com`, domain harus terdaftar dan dikonfigurasi SSL/TLS. Untuk presentasi lokal, pakai `http://rumah-batik-lili.com:5000`.

---

## STRUKTUR PROJECT

```
inventory_system/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── README.md          # Dokumentasi
└── templates/          # HTML templates
    ├── login.html
    ├── dashboard.html
    ├── barang.html
    ├── tambah_barang.html
    ├── edit_barang.html
    ├── stok.html
    ├── tambah_stok.html
    ├── transaksi.html
    ├── laporan.html
    ├── detail_transaksi.html
    └── notifikasi.html
```

---

## METODE WATERFALL

Sistem ini dibangun menggunakan metode waterfall dengan fase-fase:

1. **Requirements** - Analisis kebutuhan sistem
2. **Design** - Perancangan database dan interface
3. **Implementation** - Pengkodean sistem
4. **Verification** - Pengujian sistem
5. **Maintenance** - Pemeliharaan sistem

---

## SCREENSHOT

- Dashboard dengan statistik dan notifikasi stok
- Data barang dengan CRUD lengkap
- Transaksi penjualan dengan keranjang
- Laporan dengan filter tanggal
- Notifikasi stok habis/menipis

---

## CATATAN

- Database akan dibuat otomatis saat pertama kali dijalankan
- Sistem ini cocok untuk tugas akhir/sidang
- Tampilan modern dan responsif
- Login default: `natadi11` / `natadi11`

---

## Custom Local Link (opsional)

Jika Anda ingin menampilkan link lokal yang lebih rapi saat presentasi (mis. `http://rumah-batik-lili.com:5000`), tambahkan entri hosts di komputer Anda dan akses aplikasi pada port default Flask (5000).

1. Edit file hosts (jalankan Notepad sebagai Administrator) dan tambahkan baris berikut:

```
127.0.0.1   rumah-batik-lili.com
```

2. Jalankan aplikasi seperti biasa:

```bash
cd "c:\Users\Mumammad Harun AR\inventory_system"
python app.py
```

3. Buka browser dan kunjungi:

```
http://rumah-batik-lili.com:5000
```

Catatan:
- Jika Anda ingin tanpa menyertakan port (`:5000`), jalankan aplikasi pada port 80 (butuh hak administrator):

```powershell
# Windows (jalankan PowerShell sebagai Administrator)
python app.py --port=80
```

Atau gunakan reverse proxy (nginx/IIS) untuk mapping ke port 80.