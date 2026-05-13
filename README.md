# Netflix Cookie Checker

Bot untuk extract file RAR/ZIP/7z yang berisi cookies Netflix, lalu cek mana yang masih LIVE dan mana yang DEAD.

## Install

### Dependencies Python
```bash
pip install -r requirements.txt
```

### Tools Sistem
Skrip ini memerlukan tools untuk extract file archive:

- **unrar** (untuk file .rar):
  ```bash
  sudo apt install unrar
  ```

- **7z** (fallback untuk .rar atau untuk file .7z):
  ```bash
  sudo apt install p7zip-full
  ```

- **unzip** (untuk file .zip) - biasanya sudah terinstall di Ubuntu.

> **Catatan**: Pastikan semua tools terinstall sebelum menjalankan skrip. Jika tidak ada, skrip akan error saat extract.

## Usage

```bash
# Dari file RAR (contoh file di repo ini: cookie.rar)
cd /workspaces/codespaces-blank/netflix-checker
unrar x cookie.rar
python3 checker.py cookie.rar

# Dari folder
python3 checker.py /path/to/folder/

# Single cookie file
python3 checker.py cookie.txt
```

> Catatan: `cookie.rar` berada di folder `netflix-checker`, jadi pastikan menjalankan perintah dari folder tersebut atau gunakan path lengkap.

> Setelah menjalankan perintah, skrip akan meminta jumlah thread:
>
> ```text
> [?] Threads (default 5):
> ```
>
> Tekan Enter untuk menggunakan nilai default `5`, atau ketik angka lalu Enter.

## Format Cookie

Netscape cookie format (tab-separated):
```
.netflix.com TRUE / TRUE 1805651112 NetflixId value...
.netflix.com TRUE / TRUE 1805651112 SecureNetflixId value...
```

## Output

```
results/
├── live/    <- cookie yang masih aktif
└── dead/    <- cookie yang expired
```

Contoh output LIVE:

```
[LIVE] cookie.txt - Active account | 4K | user@example.com | BR
```

## Features

- Auto extract RAR/ZIP/7z
- Auto scan semua file, detect mana yang cookie Netflix
- Multi-threaded checking
- Hasil dipisah ke folder live/ dan dead/
- Tampilkan info akun (email, kualitas resolusi/plan, country) jika tersedia
