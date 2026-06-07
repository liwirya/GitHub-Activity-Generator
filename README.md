# GitHub Activity Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

**GitHub Activity Generator** adalah skrip Python sederhana namun *powerful* yang dirancang untuk mengisi grafik kontribusi GitHub Anda dengan riwayat *commit* buatan. Alat ini memungkinkan Anda untuk membuat profil GitHub terlihat aktif dalam hitungan menit.

> **⚠️ Disclaimer:** Script ini dibuat hanya untuk tujuan edukasi dan kesenangan semata. Jangan disalahgunakan! Keterampilan *coding* yang asli jauh lebih berharga daripada sekadar kotak hijau di profil.

---

## ✨ Fitur Utama

* **Kustomisasi Penuh:** Atur frekuensi *commit* (persentase hari aktif), jumlah maksimal *commit* per hari, dan rentang waktu (hari sebelum/sesudah).
* **Mode Realistis:** Opsi `--no_weekends` agar tidak melakukan *commit* di hari Sabtu & Minggu, sehingga terlihat seperti aktivitas normal.
* **Dukungan Push Otomatis:** Script dapat melakukan *push* otomatis ke repositori jarak jauh menggunakan koneksi yang sudah diatur (seperti SSH).
* **Konfigurasi Identitas:** Bisa mengatur `user.name` dan `user.email` khusus untuk riwayat *commit* ini secara langsung lewat argumen CLI.
* **Aman untuk README:** Skrip menggunakan file khusus (`commits.txt`) untuk *log* riwayat aktivitas, sehingga tidak akan merusak file utama repositori Anda.

---

## 🛠️ Teknologi yang Digunakan

* **Python 3**: Bahasa pemrograman utama untuk menjalankan logika skrip (*randomizer* waktu dan penanganan argumen).
* **Git**: Sistem kontrol versi untuk melakukan inisialisasi, membuat *commit*, dan *push*.
* **Bash/Shell**: Digunakan secara *native* oleh skrip untuk mengeksekusi perintah sistem di latar belakang.

---

## 📋 Prasyarat Instalasi

Sebelum menjalankan script, pastikan Anda telah memenuhi hal berikut:

1. **Python 3.x** terinstal di sistem Anda.
2. **Git** terinstal dan terkonfigurasi dengan benar.
3. **Koneksi SSH ke GitHub** (Sangat disarankan agar proses *push* berjalan otomatis tanpa perlu memasukkan *password* berulang kali).

---

## 📂 Susunan Project

* `github_activity_generator.py` / `contribute.py`: Script generator utama yang menjalankan logika.
* `LICENSE`: Berisi dokumen resmi Lisensi MIT.
* `README.md`: Dokumentasi proyek ini sendiri.

---

## 🚀 Cara Penggunaan

Anda dapat menjalankan script dengan berbagai argumen konfigurasi melalui terminal. Berikut adalah beberapa contohnya:

**1. Dasar (Push ke GitHub)**
Membuat *commit* secara default dan langsung melakukan push ke repositori.
```bash
python github_activity_generator.py -r git@github.com:username/repo.git

```

**2. Realistis (Libur akhir pekan, 60% aktif, maks 8 commit per hari)**
Membuat riwayat yang terlihat alami dan tidak seperti bot.

```bash
python github_activity_generator.py -r git@github.com:username/repo.git -nw -fr 60 -mc 8

```

**3. Hanya lokal tanpa push (Mundur 180 hari)**
Membangun riwayat hanya di direktori lokal komputer Anda tanpa mengirimnya ke GitHub.

```bash
python github_activity_generator.py -db 180 -nw

```

**4. Lihat semua opsi argumen**
Menampilkan dokumentasi dan bantuan parameter lengkap.

```bash
python github_activity_generator.py --help

```

---

## 🤝 Kontribusi

Kontribusi selalu diterima! Jika Anda ingin menambahkan fitur baru atau memperbaiki *bug*
