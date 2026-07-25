# SISTEM PENJUALAN DAN INVENTORI — RUMAH BATIK LILI
## Metode Waterfall — Tugas Akhir / Sidang

Sistem Informasi Manajemen Inventori dan Penjualan berbasis Web untuk **Rumah Batik Lili** yang dibangun dengan Metode Waterfall. Sistem ini memiliki fitur lengkap pengelolaan master barang, monitoring stok otomatis, Point of Sale (POS) kasir penjualan, laporan transaksi, dan alert notifikasi stok kritis.

---

## 🌟 Fitur Utama Sistem

| No | Fitur | Deskripsi |
|---|---|---|
| 1 | **Login Admin** | Sistem autentikasi keamanan dengan password hashing (`natadi11` / `natadi11`) |
| 2 | **Master Data Barang** | CRUD lengkap data produk batik (kode, nama, kategori, harga, stok awal, stok minimum) |
| 3 | **Monitoring & Tambah Stok** | Penambahan stok fisik barang secara real-time dengan status badge visual |
| 4 | **Transaksi Penjualan (POS)** | Kasir interaktif dengan pencarian cepat, keranjang belanja, & pengurangan stok otomatis |
| 5 | **Laporan & Struk Digital** | Laporan rekapitulasi dengan filter tanggal & cetak struk nota belanja |
| 6 | **Notifikasi Stok Kritis** | Alert otomatis real-time pada sidebar untuk barang habis/menipis |

---

## 🛠️ Teknologi Yang Digunakan

- **Backend**: Python 3 (Flask 3.0)
- **Database**: SQLite 3 (Auto-create & seeded)
- **Frontend**: HTML5, CSS3 Custom Design System (Batik Luxe Palette), JavaScript ES6 Vanilla
- **Icon Set**: Remix Icon 4.2 CDN
- **Metode Pengoperasian**: Waterfall Model

---

## 🚀 Cara Menjalankan Sistem

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
python app.py
```

### 3. Akses via Browser
Buka browser favorit Anda dan akses:
`http://localhost:5000`

---

## 🔐 Kredensial Default Login

- **Username**: `natadi11`
- **Password**: `natadi11`

---

## 🌐 Custom Local Domain (Opsional Presentasi)

Jika ingin menampilkan URL `http://rumah-batik-lili.com:5000` saat sidang:
1. Tambahkan baris ini pada file `hosts` OS Anda (`127.0.0.1 rumah-batik-lili.com`)
2. Buka `http://rumah-batik-lili.com:5000` di browser.
