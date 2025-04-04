import argparse
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import os

# Liste des ports communs
COMMON_PORTS = [
    80, 443, 8080, 8000, 8888, 5000, 7000, 8181, 8282, 3000, 4000, 9000,
    8443, 9443, 81, 591, 4711, 5800, 6080, 3001, 3002, 3003, 3004,
    4001, 4002, 2082, 2083, 2086, 2087, 2095, 2096, 8009, 8010,
    4433, 4443, 5001, 8081, 9080, 9081, 9444, 10000
]

# Bannière DirFinder
BANNER = """
██████╗ ██╗██████╗ ███████╗██╗███╗   ██╗██████╗ ███████╗██████╗        ██╗ 
██╔══██╗██║██╔══██╗██╔════╝██║████╗  ██║██╔══██╗██╔════╝██╔══██╗    ██╗╚██╗
██║  ██║██║██████╔╝█████╗  ██║██╔██╗ ██║██║  ██║█████╗  ██████╔╝    ╚═╝ ██║
██║  ██║██║██╔══██╗██╔══╝  ██║██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗    ██╗ ██║
██████╔╝██║██║  ██║██║     ██║██║ ╚████║██████╔╝███████╗██║  ██║    ╚═╝██╔╝
╚═════╝ ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝       ╚═╝  
"""

def check_directory(base_url, directory):
    """
    Teste un répertoire sur une URL donnée.
    """
    full_url = f"{base_url}/{directory}"
    try:
        response = requests.get(full_url, timeout=5)
        if response.status_code in [200, 301, 302]:
            return f"[+] Found: {full_url} ({response.status_code})"
    except requests.RequestException:
        pass
    return None

def load_wordlist(wordlist_path):
    """
    Charge les mots depuis un fichier wordlist.
    """
    if not os.path.exists(wordlist_path):
        print(f"[!] Wordlist not found: {wordlist_path}")
        return []
    with open(wordlist_path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def discover_port(target_ip):
    """
    Tente de découvrir un port ouvert sur l'IP cible en testant des ports communs.
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

def main():
    # Affichage de la bannière
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="A simple directory brute-forcing tool, à la manière de DirBuster."
    )
    parser.add_argument("-u", "--url", required=True, help="Target URL or IP, with optional path (e.g., http://example.com or http://example.com/path/)")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to the wordlist file")
    parser.add_argument("-p", "--port", type=int, help="Specify the port of the web service (default: auto-discover)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("-o", "--output", help="Output file to save the results (default: None)", default=None)
    
    args = parser.parse_args()

    base_url = args.url.rstrip("/")  # Assure que l'URL de base ne finit pas par "/"
    wordlist = load_wordlist(args.wordlist)
    if not wordlist:
        print("[!] Wordlist is empty or invalid. Exiting.")
        return

    # Découvrir le port si non spécifié
    port = args.port
    if port is None:
        target_ip = base_url.replace("http://", "").replace("https://", "").split("/")[0]
        port = discover_port(target_ip)
        if not port:
            return
        base_url = f"http://{target_ip}:{port}" + base_url[len(f"http://{target_ip}"):]  # Conserver le chemin initial
    
    print(f"[+] Scanning: {base_url}")
    print(f"[+] Using wordlist: {args.wordlist}")
    print(f"[+] Threads: {args.threads}")

    # Initialisation du fichier de sortie si fourni
    if args.output:
        output_file = open(args.output, "w")
        print(f"[+] Results will be saved to: {args.output}")
    else:
        output_file = None

    # Barre de progression
    total_directories = len(wordlist)
    progress_bar = tqdm(total=total_directories, desc="Scanning directories", ncols=100, dynamic_ncols=True, position=0, leave=True)

    # Scanner les répertoires
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        future_to_directory = {executor.submit(check_directory, base_url, directory): directory for directory in wordlist}

        for future in as_completed(future_to_directory):
            result = future.result()
            if result:
                print(result)  # Affiche uniquement les répertoires trouvés
                if output_file:
                    output_file.write(result + "\n")  # Sauvegarde dans le fichier

            progress_bar.update(1)  # Mise à jour de la barre de progression

    progress_bar.close()

    if output_file:
        output_file.close()

    print("[*] Scan completed.")

if __name__ == "__main__":
    main()
