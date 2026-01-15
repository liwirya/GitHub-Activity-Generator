# GitHub Activity Generator 

Script Python sederhana untuk membuat **fake commit history** di GitHub kamu. 
Buat profil GitHub-mu jadi hijau semua dalam hitungan menit! 🟩🟩🟩

## ✨ Fitur
- **Termux Optimized:** Ringan dan tidak bikin HP nge-hang.
- **Progress Bar:** Tampilan persentase proses biar gak dikira macet.
- **Customizable:** Atur frekuensi, hari libur, dan jumlah commit per hari.
- **SSH Support:** Push otomatis menggunakan SSH key.

## 🛠️ Persiapan (Wajib!)

Sebelum pakai, pastikan kamu sudah punya Python, Git, dan **SSH Key** yang terkoneksi ke GitHub.

### 1. Install Paket
Buka Termux Atau Vps dan jalankan:
```bash
pkg update && pkg upgrade
pkg install python git openssh
```

2. Setting SSH Key (PENTING)
Agar script bisa nge-push ke GitHub tanpa password, kamu harus setting SSH dulu.
 * Generate Key:
   ```bash
   ssh-keygen -t ed25519 -C "email-github-mu@gmail.com"
   ```
   (Tekan ENTER terus sampai selesai)
   
 * Ambil Key Publik:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   Copy semua teks yang muncul (dimulai dari ssh-ed25519...).
 
 * Masukan ke GitHub:
   * Buka GitHub Settings > SSH Keys.
   * Klik New SSH Key.
   * Paste key tadi di kolom "Key", lalu Save.
 
 * Tes Koneksi:
   Di Termux atau Vps ketik:
   ```bash
   ssh -T git@github.com
   ```
   Ketikan yes / enter jika ditanya. Kalau sukses muncul tulisan "Hi username! You've successfully authenticated".
   
# 🚀 Cara Pakai

1. Clone Repo Ini
```bash
git clone https://github.com/liwirya/GitHub-Activity-Generator.git
cd GitHub-Activity-Generator
```

2. Jalankan Script
Ada dua cara pakai, mode Basic (brutal) atau Realistic (santai).

A. Mode Realistic (Rekomendasi) 🌟
Kelihatan seperti developer asli. Ada hari libur (weekend) dan bolong-bolong dikit.
```bash
python contribute.py --max_commits=12 --frequency=60 --no_weekends --repository=git@github.com:USERNAME/NAMA-REPO-TARGET.git
```
Penjelasan:
 * --max_commits=12: Maksimal 12 commit dalam sehari.
 * --frequency=60: Rajin ngoding 60% dalam setahun (40% rebahan).
 * --no_weekends: Sabtu & Minggu libur coding.

B. Mode Brutal (Hijau Semua) 🔥
Full commit setiap hari tanpa libur.
```bash
python contribute.py --repository=git@github.com:USERNAME/NAMA-REPO-TARGET.git
```

3. Tunggu Prosesnya
Script akan memproses ratusan/ribuan commit.
 * Tunggu sampai 100%.
 * Script akan otomatis melakukan git push di akhir.
 * Cek profil GitHub kamu setelah selesai!

# ⚠️ Disclaimer
Script ini dibuat untuk tujuan edukasi dan fun semata. Jangan gunakan untuk menipu rekruter atau klien bahwa kamu sangat aktif, padahal cuma bot. Skill asli lebih penting daripada kotak hijau! 😉
Modified for Termux usability.