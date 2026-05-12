# Netflix Cookie Checker

Bot untuk extract file RAR/ZIP/7z yang berisi cookies Netflix, lalu cek mana yang masih LIVE dan mana yang DEAD.

## Install

```bash
pip install -r requirements.txt
sudo apt install unrar
```

## Usage

```bash
# Dari file RAR
python3 checker.py cookies.rar

# Dari folder
python3 checker.py /path/to/folder/

# Single cookie file
python3 checker.py cookie.txt
```

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

## Features

- Auto extract RAR/ZIP/7z
- Auto scan semua file, detect mana yang cookie Netflix
- Multi-threaded checking
- Hasil dipisah ke folder live/ dan dead/
- Tampilkan info akun (email, plan, country) jika tersedia