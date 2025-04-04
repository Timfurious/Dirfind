# 🔍 DirFinder - A Simple and Efficient Directory Brute-Forcing Tool

# DirFinder is a lightweight, multi-threaded directory brute-forcing tool designed for security researchers and penetration testers. It helps discover hidden directories and files on web servers by testing a given wordlist 

# against the target URL. Inspired by DirBuster, this tool efficiently scans for accessible paths using concurrent requests, automatic port detection, and a real-time progress bar.

🚀 Features
✅ Automatic Port Discovery: If no port is specified, DirFinder scans common web ports to find an open service.

✅ Multi-threaded Scanning: Uses ThreadPoolExecutor for high-speed directory enumeration.

✅ Real-time Progress Bar: Displays the scanning progress dynamically with tqdm.

✅ Custom Wordlists: Users can provide their own wordlist for flexible and extensive scanning.

✅ Error Handling: Gracefully handles request timeouts and failed connections.

✅ Output File Support: Optionally save found directories to a file.

✅ Lightweight & Easy to Use: Requires minimal dependencies and runs efficiently.


🛠️ Installation
get python

git clone https://github.com/yourusername/DirFind.git  

cd DirFind

🔍 Usage

📌 Basic Scan

Run a simple directory brute-force scan with a target URL and a wordlist:

python dirfinder.py -u http://example.com -w wordlist.txt

📌 Additional Options

Option	Description	Example

-p, --port	Specify the target port manually	-p 8080

-t, --threads	Set the number of concurrent threads (default: 10)	-t 20

-o, --output	Save the results to a file	-o results.txt

--no-verify For not verifying the ssl

--recursive Follow directorys and search in

Example Usage:

python dirfinder.py -u http://example.com -w wordlist.txt -p 8080 -t 20 -o found_dirs.txt --recursive --no-verify

🎥 screenshots 

![photo](https://github.com/user-attachments/assets/e81e5d73-5258-4d46-a075-3ee7fee57292)

