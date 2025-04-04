import argparse
import requests
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# Common web ports
COMMON_PORTS = [
    80, 443, 8080, 8000, 8888, 5000, 7000, 8181, 8282, 3000, 4000, 9000,
    8443, 9443, 81, 591, 4711, 5800, 6080, 3001, 3002, 3003, 3004,
    4001, 4002, 2082, 2083, 2086, 2087, 2095, 2096, 8009, 8010,
    4433, 4443, 5001, 8081, 9080, 9081, 9444, 10000
]

# Random User-Agent list
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36"
]

# Banner
BANNER = """
██████╗ ██╗██████╗ ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗        ██╗ 
██╔══██╗██║██╔══██╗██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗    ██╗╚██╗
██║  ██║██║██████╔╝█████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝    ╚═╝ ██║
██║  ██║██║██╔══██╗██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗    ██╗ ██║
██████╔╝██║██║  ██║██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║    ╚═╝██╔╝
╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝       ╚═╝  
"""

def check_directory(base_url, directory, headers, verify_ssl):
    """
    Tests a directory on a given URL.
    """
    full_url = f"{base_url}/{directory}"
    try:
        response = requests.get(full_url, headers=headers, timeout=5, verify=verify_ssl)
        if response.status_code in [200, 301, 302]:
            return f"[+] Found: {full_url} ({response.status_code})"
    except requests.RequestException:
        pass
    return None

def load_wordlist(wordlist_path):
    """
    Loads words from a wordlist file.
    """
    if not os.path.exists(wordlist_path):
        print(f"[!] Wordlist not found: {wordlist_path}")
        return []
    with open(wordlist_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def discover_port(target_ip):
    """
    Attempts to discover an open port on the target IP.
    """
    print("[*] Searching for open web ports...")
    for port in COMMON_PORTS:
        try:
            response = requests.get(f"http://{target_ip}:{port}", timeout=2)
            if response.status_code in [200, 301, 302]:
                print(f"[+] Web service found on port {port}")
                return port
        except requests.RequestException:
            continue
    print("[!] No open web ports found. Exiting.")
    return None

def recursive_scan(base_url, found_directories, headers, verify_ssl):
    """
    Recursively scans newly found directories for more subdirectories.
    """
    print("\n[*] Starting recursive scan...")
    new_dirs = found_directories.copy()
    
    for directory in new_dirs:
        new_url = f"{base_url}/{directory}"
        for word in found_directories:
            full_url = f"{new_url}/{word}"
            try:
                response = requests.get(full_url, headers=headers, timeout=5, verify=verify_ssl)
                if response.status_code in [200, 301, 302]:
                    print(f"[++] Recursive Found: {full_url} ({response.status_code})")
                    found_directories.append(f"{directory}/{word}")
            except requests.RequestException:
                continue

def main():
    # Display banner
    print(BANNER)

    parser = argparse.ArgumentParser(description="A simple directory brute-forcing tool, à la manière de DirBuster.")
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g., http://example.com)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file")
    parser.add_argument("-p", "--port", type=int, help="Specify the web service port (default: auto-discover)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-o", "--output", help="Output file to save the results", default=None)
    parser.add_argument("--no-verify", action="store_true", help="Disable SSL verification")
    parser.add_argument("--recursive", action="store_true", help="Enable recursive scanning")

    args = parser.parse_args()

    base_url = args.url.rstrip("/")  # Ensure base URL does not end with "/"
    wordlist = load_wordlist(args.wordlist)
    if not wordlist:
        print("[!] Wordlist is empty or invalid. Exiting.")
        return

    port = args.port
    if port is None:
        target_ip = base_url.replace("http://", "").replace("https://", "").split("/")[0]
        port = discover_port(target_ip)
        if not port:
            return
        base_url = f"http://{target_ip}:{port}" + base_url[len(f"http://{target_ip}"):]

    print(f"[+] Scanning: {base_url}")
    print(f"[+] Using wordlist: {args.wordlist}")
    print(f"[+] Threads: {args.threads}")
    
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    verify_ssl = not args.no_verify

    output_file = open(args.output, "w") if args.output else None

    found_directories = []
    progress_bar = tqdm(total=len(wordlist), desc="Scanning directories", ncols=100, dynamic_ncols=True)

    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = {executor.submit(check_directory, base_url, word, headers, verify_ssl): word for word in wordlist}

        for future in as_completed(futures):
            result = future.result()
            if result:
                print(result)
                found_directories.append(futures[future])
                if output_file:
                    output_file.write(result + "\n")
            progress_bar.update(1)

    progress_bar.close()
    
    if args.recursive and found_directories:
        recursive_scan(base_url, found_directories, headers, verify_ssl)

    if output_file:
        output_file.close()

    print("[*] Scan completed.")

if __name__ == "__main__":
    main()
