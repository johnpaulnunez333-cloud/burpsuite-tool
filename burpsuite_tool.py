import os
import sys
import socket
import threading
import time
import json
import ssl
from datetime import datetime
from urllib.parse import urlparse, parse_qs
try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import requests
except ImportError:
    print("Installing required dependencies...")
    os.system('pip install requests')
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import requests

BLOOD = '\033[91m'
BRIGHT_RED = '\033[1;91m'
WHITE = '\033[97m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

captured_requests = []
intercepted_queue = []
proxy_running = False
proxy_thread = None
proxy_filter_domain = None

def clear_screen():
    os.system('clear' if os.name != 'nt' else 'cls')

def show_banner():
    clear_screen()
    print(f"{BLOOD}{BOLD}")
    print(r"")
    print(r"  ██████╗ ██╗   ██╗██████╗ ██████╗ ███████╗██╗   ██╗██╗████████╗███████╗")
    print(r"  ██╔══██╗██║   ██║██╔══██╗██╔══██╗██╔════╝██║   ██║██║╚══██╔══╝██╔════╝")
    print(r"  ██████╔╝██║   ██║██████╔╝██████╔╝███████╗██║   ██║██║   ██║   █████╗  ")
    print(r"  ██╔══██╗██║   ██║██╔══██╗██╔═══╝ ╚════██║██║   ██║██║   ██║   ██╔══╝  ")
    print(r"  ██████╔╝╚██████╔╝██║  ██║██║     ███████║╚██████╔╝██║   ██║   ███████╗")
    print(r"  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚══════╝ ╚═════╝ ╚═╝   ╚═╝   ╚══════╝")
    print(r"")
    print(f"{WHITE}{'═'*80}")
    print(f"{BRIGHT_RED}          🔥 PROFESSIONAL HTTP INTERCEPTION & ANALYSIS TOOL")
    print(f"{GREEN}          ⚡ PROXY MODE | PACKET CAPTURE | REQUEST MANIPULATION")
    print(f"{YELLOW}          🛡️  SUPPORTS ROOTED & NON-ROOTED DEVICES")
    print(f"{WHITE}{'═'*80}{RESET}\n")

class ProxyHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
        pass
    
    def do_GET(self):
        self.handle_request('GET')
    
    def do_POST(self):
        self.handle_request('POST')
    
    def do_PUT(self):
        self.handle_request('PUT')
    
    def do_DELETE(self):
        self.handle_request('DELETE')
    
    def do_OPTIONS(self):
        self.handle_request('OPTIONS')
    
    def do_HEAD(self):
        self.handle_request('HEAD')
    
    def handle_request(self, method):
        global captured_requests, intercepted_queue, proxy_filter_domain
        
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b''
        
        url = self.path
        if not url.startswith('http'):
            url = f"http://{self.headers.get('Host', 'localhost')}{self.path}"
        
        host = self.headers.get('Host', 'unknown')
        
        if proxy_filter_domain:
            if proxy_filter_domain not in host:
                try:
                    headers = dict(self.headers)
                    headers.pop('Host', None)
                    
                    response = requests.request(
                        method=method,
                        url=url,
                        headers=headers,
                        data=body,
                        allow_redirects=False,
                        verify=False,
                        timeout=10
                    )
                    
                    self.send_response(response.status_code)
                    for header, value in response.headers.items():
                        if header.lower() not in ['transfer-encoding', 'connection']:
                            self.send_header(header, value)
                    self.end_headers()
                    self.wfile.write(response.content)
                except:
                    pass
                return
        
        request_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'method': method,
            'url': url,
            'headers': dict(self.headers),
            'body': body.decode('utf-8', errors='ignore') if body else '',
            'host': host,
            'path': self.path
        }
        
        captured_requests.append(request_data)
        
        filter_msg = f" [FILTERED: {proxy_filter_domain}]" if proxy_filter_domain else ""
        print(f"{CYAN}[CAPTURED]{filter_msg}{RESET} {method} {url[:60]}")
        
        try:
            headers = dict(self.headers)
            headers.pop('Host', None)
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                allow_redirects=False,
                verify=False,
                timeout=10
            )
            
            self.send_response(response.status_code)
            for header, value in response.headers.items():
                if header.lower() not in ['transfer-encoding', 'connection']:
                    self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_error(502, f"Proxy Error: {str(e)}")

def start_proxy_server(port=8080):
    global proxy_running, proxy_thread
    
    try:
        server = HTTPServer(('0.0.0.0', port), ProxyHandler)
        proxy_running = True
        print(f"{GREEN}[+] Proxy server started on port {port}{RESET}")
        print(f"{YELLOW}[*] Configure your device to use proxy: localhost:{port}{RESET}")
        print(f"{CYAN}[*] Press Ctrl+C to stop the proxy{RESET}\n")
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[*] Stopping proxy server...{RESET}")
        proxy_running = False
    except Exception as e:
        print(f"{BLOOD}[ERROR] Failed to start proxy: {e}{RESET}")
        proxy_running = False

def view_captured_requests():
    show_banner()
    
    if not captured_requests:
        print(f"{YELLOW}[!] No captured requests yet{RESET}")
        print(f"{CYAN}[*] Start the proxy and configure your device to capture traffic{RESET}\n")
        input(f"{GREEN}Press Enter to return...{RESET}")
        return
    
    print(f"{BRIGHT_RED}{BOLD}CAPTURED REQUESTS ({len(captured_requests)} total){RESET}")
    print(f"{WHITE}{'═'*80}{RESET}\n")
    
    for idx, req in enumerate(captured_requests[-20:], 1):
        print(f"{CYAN}[{idx}]{RESET} {req['method']} - {req['url'][:60]}")
        print(f"    Time: {req['timestamp']} | Host: {req['host']}")
    
    print(f"\n{WHITE}{'═'*80}{RESET}")
    
    choice = input(f"\n{GREEN}Enter request number to view details (or Enter to return): {RESET}")
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(captured_requests[-20:]):
            view_request_details(captured_requests[-(20-idx)])
        else:
            print(f"{BLOOD}[!] Invalid request number{RESET}")
            time.sleep(1)

def view_request_details(request):
    show_banner()
    print(f"{BRIGHT_RED}{BOLD}REQUEST DETAILS{RESET}")
    print(f"{WHITE}{'═'*80}{RESET}\n")
    
    print(f"{CYAN}Method:{RESET}    {request['method']}")
    print(f"{CYAN}URL:{RESET}       {request['url']}")
    print(f"{CYAN}Time:{RESET}      {request['timestamp']}")
    print(f"{CYAN}Host:{RESET}      {request['host']}")
    print(f"{CYAN}Path:{RESET}      {request['path']}")
    
    print(f"\n{BRIGHT_RED}HEADERS:{RESET}")
    print(f"{WHITE}{'-'*80}{RESET}")
    for header, value in request['headers'].items():
        print(f"{YELLOW}{header}:{RESET} {value}")
    
    if request['body']:
        print(f"\n{BRIGHT_RED}BODY:{RESET}")
        print(f"{WHITE}{'-'*80}{RESET}")
        print(f"{GREEN}{request['body'][:500]}{RESET}")
        if len(request['body']) > 500:
            print(f"{YELLOW}... (truncated){RESET}")
    
    print(f"\n{WHITE}{'═'*80}{RESET}")
    
    print(f"\n{CYAN}[1]{RESET} Save to file")
    print(f"{CYAN}[2]{RESET} Copy URL")
    print(f"{CYAN}[3]{RESET} Return to list")
    
    choice = input(f"\n{GREEN}Select option: {RESET}")
    
    if choice == '1':
        filename = f"request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(request, f, indent=2)
        print(f"{GREEN}[+] Saved to {filename}{RESET}")
        time.sleep(2)
    elif choice == '2':
        print(f"{GREEN}URL: {request['url']}{RESET}")
        input(f"{CYAN}Press Enter to continue...{RESET}")

def export_all_requests():
    show_banner()
    
    if not captured_requests:
        print(f"{YELLOW}[!] No requests to export{RESET}")
        input(f"{GREEN}Press Enter to return...{RESET}")
        return
    
    filename = f"burpsuite_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(captured_requests, f, indent=2)
        
        print(f"{GREEN}[+] Exported {len(captured_requests)} requests{RESET}")
        print(f"{CYAN}[+] File: {filename}{RESET}")
        print(f"{YELLOW}[+] Size: {os.path.getsize(filename)} bytes{RESET}")
    except Exception as e:
        print(f"{BLOOD}[ERROR] Export failed: {e}{RESET}")
    
    input(f"\n{GREEN}Press Enter to return...{RESET}")

def packet_sniffer_mode():
    show_banner()
    print(f"{BRIGHT_RED}{BOLD}PACKET SNIFFER MODE{RESET}")
    print(f"{WHITE}{'═'*80}{RESET}\n")
    
    try:
        import scapy.all as scapy
        sniffer_available = True
    except ImportError:
        sniffer_available = False
    
    if not sniffer_available:
        print(f"{YELLOW}[!] Scapy not installed - Installing...{RESET}")
        os.system('pip install scapy')
        try:
            import scapy.all as scapy
            sniffer_available = True
        except:
            print(f"{BLOOD}[ERROR] Failed to install scapy{RESET}")
            print(f"{YELLOW}[*] Install manually: pip install scapy{RESET}")
            input(f"\n{GREEN}Press Enter to return...{RESET}")
            return
    
    print(f"{GREEN}[+] Packet sniffer ready{RESET}")
    print(f"{CYAN}[*] Capturing HTTP/HTTPS packets...{RESET}")
    print(f"{YELLOW}[*] Press Ctrl+C to stop{RESET}\n")
    
    def packet_handler(packet):
        if packet.haslayer(scapy.TCP) and packet.haslayer(scapy.Raw):
            try:
                payload = packet[scapy.Raw].load.decode('utf-8', errors='ignore')
                
                if 'HTTP' in payload or 'GET' in payload or 'POST' in payload:
                    src_ip = packet[scapy.IP].src if packet.haslayer(scapy.IP) else 'unknown'
                    dst_ip = packet[scapy.IP].dst if packet.haslayer(scapy.IP) else 'unknown'
                    
                    print(f"{CYAN}[PACKET]{RESET} {src_ip} → {dst_ip}")
                    
                    lines = payload.split('\r\n')
                    if lines:
                        print(f"{GREEN}  {lines[0][:70]}{RESET}")
            except:
                pass
    
    try:
        scapy.sniff(filter="tcp port 80 or tcp port 443", prn=packet_handler, store=0)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[*] Stopped packet capture{RESET}")
        input(f"{GREEN}Press Enter to return...{RESET}")
    except Exception as e:
        print(f"{BLOOD}[ERROR] Sniffer error: {e}{RESET}")
        print(f"{YELLOW}[*] Root privileges may be required{RESET}")
        input(f"\n{GREEN}Press Enter to return...{RESET}")

def repeater_mode():
    show_banner()
    print(f"{BRIGHT_RED}{BOLD}HTTP REPEATER{RESET}")
    print(f"{WHITE}{'═'*80}{RESET}\n")
    
    url = input(f"{CYAN}Enter URL: {RESET}").strip()
    if not url:
        return
    
    method = input(f"{CYAN}Method (GET/POST/PUT/DELETE) [GET]: {RESET}").strip().upper() or 'GET'
    
    print(f"\n{YELLOW}Enter headers (format: Key: Value, empty line to finish):{RESET}")
    headers = {}
    while True:
        header = input(f"{GREEN}> {RESET}").strip()
        if not header:
            break
        if ':' in header:
            key, value = header.split(':', 1)
            headers[key.strip()] = value.strip()
    
    body = ""
    if method in ['POST', 'PUT']:
        print(f"\n{YELLOW}Enter body (empty line to finish):{RESET}")
        lines = []
        while True:
            line = input(f"{GREEN}> {RESET}")
            if not line:
                break
            lines.append(line)
        body = '\n'.join(lines)
    
    print(f"\n{CYAN}[*] Sending request...{RESET}\n")
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            data=body,
            verify=False,
            timeout=10
        )
        
        print(f"{BRIGHT_RED}RESPONSE:{RESET}")
        print(f"{WHITE}{'═'*80}{RESET}")
        print(f"{CYAN}Status:{RESET} {response.status_code} {response.reason}")
        print(f"{CYAN}Time:{RESET} {response.elapsed.total_seconds():.2f}s")
        print(f"{CYAN}Size:{RESET} {len(response.content)} bytes")
        
        print(f"\n{BRIGHT_RED}HEADERS:{RESET}")
        print(f"{WHITE}{'-'*80}{RESET}")
        for header, value in response.headers.items():
            print(f"{YELLOW}{header}:{RESET} {value}")
        
        print(f"\n{BRIGHT_RED}BODY:{RESET}")
        print(f"{WHITE}{'-'*80}{RESET}")
        content = response.text[:1000]
        print(f"{GREEN}{content}{RESET}")
        if len(response.text) > 1000:
            print(f"{YELLOW}... (truncated){RESET}")
        
    except Exception as e:
        print(f"{BLOOD}[ERROR] Request failed: {e}{RESET}")
    
    input(f"\n{GREEN}Press Enter to return...{RESET}")

def intruder_mode():
    show_banner()
    print(f"{BRIGHT_RED}{BOLD}HTTP INTRUDER (FUZZER){RESET}")
    print(f"{WHITE}{'═'*80}{RESET}\n")
    
    url_template = input(f"{CYAN}Enter URL with {{FUZZ}} marker: {RESET}").strip()
    if not url_template or '{FUZZ}' not in url_template:
        print(f"{BLOOD}[ERROR] URL must contain {{FUZZ}} marker{RESET}")
        input(f"{GREEN}Press Enter to return...{RESET}")
        return
    
    print(f"\n{YELLOW}Enter payloads (one per line, empty line to finish):{RESET}")
    payloads = []
    while True:
        payload = input(f"{GREEN}> {RESET}").strip()
        if not payload:
            break
        payloads.append(payload)
    
    if not payloads:
        print(f"{BLOOD}[ERROR] No payloads provided{RESET}")
        input(f"{GREEN}Press Enter to return...{RESET}")
        return
    
    print(f"\n{CYAN}[*] Starting attack with {len(payloads)} payloads...{RESET}\n")
    
    results = []
    for idx, payload in enumerate(payloads, 1):
        url = url_template.replace('{FUZZ}', payload)
        
        try:
            response = requests.get(url, timeout=5, verify=False)
            status = response.status_code
            length = len(response.content)
            
            color = GREEN if status == 200 else YELLOW if status in [301, 302] else BLOOD
            
            print(f"{color}[{idx}/{len(payloads)}]{RESET} {payload:20} → Status: {status} | Size: {length}")
            
            results.append({
                'payload': payload,
                'url': url,
                'status': status,
                'length': length,
                'time': response.elapsed.total_seconds()
            })
            
        except Exception as e:
            print(f"{BLOOD}[{idx}/{len(payloads)}]{RESET} {payload:20} → Error: {str(e)[:30]}")
    
    print(f"\n{WHITE}{'═'*80}{RESET}")
    print(f"{GREEN}[+] Attack completed: {len(results)} successful requests{RESET}")
    
    save = input(f"\n{CYAN}Save results? (y/n): {RESET}").strip().lower()
    if save == 'y':
        filename = f"intruder_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"{GREEN}[+] Saved to {filename}{RESET}")
    
    input(f"\n{GREEN}Press Enter to return...{RESET}")

def proxy_mode():
    show_banner()
    print(f"{BRIGHT_RED}{BOLD}AUTOMATED SECURITY SCANNER{RESET}")
    print(f"{WHITE}{'═'*80}{RESET}\n")
    
    target_url = input(f"{CYAN}Enter target URL to scan: {RESET}").strip()
    
    if not target_url:
        print(f"{BLOOD}[ERROR] URL is required!{RESET}")
        input(f"{GREEN}Press Enter to return...{RESET}")
        return
    
    if not target_url.startswith('http'):
        target_url = 'https://' + target_url
    
    from urllib.parse import urlparse
    parsed = urlparse(target_url)
    domain = parsed.netloc
    base_path = parsed.path or '/'
    
    print(f"\n{BRIGHT_RED}SCAN CONFIGURATION:{RESET}")
    print(f"{WHITE}{'═'*80}{RESET}")
    print(f"{CYAN}Target:{RESET}      {target_url}")
    print(f"{CYAN}Domain:{RESET}      {domain}")
    print(f"{CYAN}Protocol:{RESET}    {parsed.scheme}")
    print(f"{WHITE}{'═'*80}{RESET}\n")
    
    print(f"{YELLOW}SCAN TYPES:{RESET}")
    print(f"{GREEN}[1] Quick Scan        - Fast security check (5 tests){RESET}")
    print(f"{GREEN}[2] Full Scan         - Comprehensive analysis (20+ tests){RESET}")
    print(f"{GREEN}[3] Vulnerability Scan - Deep security audit (50+ tests){RESET}")
    
    scan_type = input(f"\n{CYAN}Select scan type [1]: {RESET}").strip() or "1"
    
    print(f"\n{YELLOW}[*] Starting automated scan...{RESET}\n")
    time.sleep(1)
    
    results = []
    
    print(f"{BRIGHT_RED}{'='*80}")
    print(f"AUTOMATED SECURITY SCAN RESULTS")
    print(f"{'='*80}{RESET}\n")
    
    if scan_type == "1":
        tests = [
            ("HTTP Response", target_url),
            ("SSL/TLS Check", target_url),
            ("Security Headers", target_url),
            ("Server Info", target_url),
            ("Common Paths", f"{target_url}/admin")
        ]
    elif scan_type == "2":
        tests = [
            ("HTTP Response", target_url),
            ("SSL/TLS Check", target_url),
            ("Security Headers", target_url),
            ("Server Info", target_url),
            ("Admin Panel", f"{parsed.scheme}://{domain}/admin"),
            ("Login Page", f"{parsed.scheme}://{domain}/login"),
            ("API Endpoint", f"{parsed.scheme}://{domain}/api"),
            ("Config Files", f"{parsed.scheme}://{domain}/config.php"),
            ("Backup Files", f"{parsed.scheme}://{domain}/backup.sql"),
            ("phpinfo", f"{parsed.scheme}://{domain}/phpinfo.php"),
            ("Test Pages", f"{parsed.scheme}://{domain}/test"),
            ("Debug Mode", f"{parsed.scheme}://{domain}/debug"),
            ("WordPress", f"{parsed.scheme}://{domain}/wp-admin"),
            ("Database", f"{parsed.scheme}://{domain}/phpmyadmin"),
            ("Git Repo", f"{parsed.scheme}://{domain}/.git/config"),
            ("Env File", f"{parsed.scheme}://{domain}/.env"),
            ("Robots.txt", f"{parsed.scheme}://{domain}/robots.txt"),
            ("Sitemap", f"{parsed.scheme}://{domain}/sitemap.xml"),
            ("CORS Check", target_url),
            ("Rate Limiting", target_url)
        ]
    else:
        tests = [
            ("HTTP Response", target_url),
            ("HTTPS Redirect", target_url.replace('https://', 'http://')),
            ("SSL/TLS Version", target_url),
            ("Certificate Validity", target_url),
            ("Security Headers", target_url),
            ("HSTS Header", target_url),
            ("CSP Header", target_url),
            ("X-Frame-Options", target_url),
            ("Server Info", target_url),
            ("Admin Panel", f"{parsed.scheme}://{domain}/admin"),
            ("Administrator", f"{parsed.scheme}://{domain}/administrator"),
            ("Login", f"{parsed.scheme}://{domain}/login"),
            ("Auth", f"{parsed.scheme}://{domain}/auth"),
            ("API v1", f"{parsed.scheme}://{domain}/api/v1"),
            ("API v2", f"{parsed.scheme}://{domain}/api/v2"),
            ("GraphQL", f"{parsed.scheme}://{domain}/graphql"),
            ("Config", f"{parsed.scheme}://{domain}/config.php"),
            ("Settings", f"{parsed.scheme}://{domain}/settings.php"),
            ("Backup", f"{parsed.scheme}://{domain}/backup.sql"),
            ("Database", f"{parsed.scheme}://{domain}/db.sql"),
            ("phpinfo", f"{parsed.scheme}://{domain}/phpinfo.php"),
            ("info.php", f"{parsed.scheme}://{domain}/info.php"),
            ("Test", f"{parsed.scheme}://{domain}/test"),
            ("Debug", f"{parsed.scheme}://{domain}/debug"),
            ("WordPress Login", f"{parsed.scheme}://{domain}/wp-login.php"),
            ("WP Admin", f"{parsed.scheme}://{domain}/wp-admin"),
            ("Joomla", f"{parsed.scheme}://{domain}/administrator"),
            ("Drupal", f"{parsed.scheme}://{domain}/user/login"),
            ("phpMyAdmin", f"{parsed.scheme}://{domain}/phpmyadmin"),
            ("Adminer", f"{parsed.scheme}://{domain}/adminer.php"),
            (".git folder", f"{parsed.scheme}://{domain}/.git/config"),
            (".svn folder", f"{parsed.scheme}://{domain}/.svn/entries"),
            (".env file", f"{parsed.scheme}://{domain}/.env"),
            (".htaccess", f"{parsed.scheme}://{domain}/.htaccess"),
            ("web.config", f"{parsed.scheme}://{domain}/web.config"),
            ("package.json", f"{parsed.scheme}://{domain}/package.json"),
            ("composer.json", f"{parsed.scheme}://{domain}/composer.json"),
            ("Dockerfile", f"{parsed.scheme}://{domain}/Dockerfile"),
            ("README.md", f"{parsed.scheme}://{domain}/README.md"),
            ("robots.txt", f"{parsed.scheme}://{domain}/robots.txt"),
            ("sitemap.xml", f"{parsed.scheme}://{domain}/sitemap.xml"),
            ("humans.txt", f"{parsed.scheme}://{domain}/humans.txt"),
            ("security.txt", f"{parsed.scheme}://{domain}/.well-known/security.txt"),
            ("CORS Policy", target_url),
            ("Rate Limiting", target_url),
            ("Session Handling", target_url),
            ("Cookie Security", target_url),
            ("XSS Protection", target_url),
            ("SQL Injection Test", f"{target_url}?id=1'"),
            ("Path Traversal", f"{target_url}?file=../../../etc/passwd")
        ]
    
    vulnerabilities = []
    warnings = []
    info_items = []
    
    for idx, (test_name, test_url) in enumerate(tests, 1):
        print(f"{CYAN}[{idx}/{len(tests)}]{RESET} Testing: {test_name}...", end=' ')
        
        try:
            response = requests.get(test_url, timeout=5, verify=False, allow_redirects=True)
            status = response.status_code
            size = len(response.content)
            
            if status == 200:
                if test_name in ["Admin Panel", "Administrator", "Login", "phpinfo", "Config", "Backup", "Database", ".git folder", ".env file"]:
                    print(f"{BLOOD}VULNERABLE! (Status: {status}){RESET}")
                    vulnerabilities.append({
                        'test': test_name,
                        'url': test_url,
                        'status': status,
                        'size': size,
                        'severity': 'HIGH'
                    })
                else:
                    print(f"{GREEN}OK (Status: {status}){RESET}")
                    info_items.append({
                        'test': test_name,
                        'url': test_url,
                        'status': status,
                        'size': size
                    })
            elif status == 403:
                print(f"{YELLOW}PROTECTED (Status: {status}){RESET}")
                warnings.append({
                    'test': test_name,
                    'url': test_url,
                    'status': status,
                    'severity': 'MEDIUM'
                })
            elif status == 404:
                print(f"{WHITE}Not Found (Status: {status}){RESET}")
            else:
                print(f"{CYAN}Status: {status}{RESET}")
            
            results.append({
                'test': test_name,
                'url': test_url,
                'status': status,
                'size': size
            })
            
        except Exception as e:
            print(f"{BLOOD}ERROR{RESET}")
        
        time.sleep(0.2)
    
    print(f"\n{BRIGHT_RED}{'='*80}")
    print(f"SCAN SUMMARY")
    print(f"{'='*80}{RESET}\n")
    
    if vulnerabilities:
        print(f"{BLOOD}{BOLD}HIGH RISK VULNERABILITIES FOUND: {len(vulnerabilities)}{RESET}")
        for vuln in vulnerabilities:
            print(f"{BLOOD}  [!] {vuln['test']}: {vuln['url']}{RESET}")
            print(f"      Status: {vuln['status']} | Size: {vuln['size']} bytes")
    
    if warnings:
        print(f"\n{YELLOW}{BOLD}WARNINGS: {len(warnings)}{RESET}")
        for warn in warnings:
            print(f"{YELLOW}  [*] {warn['test']}: Protected but exists{RESET}")
    
    print(f"\n{CYAN}Total Tests: {len(tests)}{RESET}")
    print(f"{GREEN}Passed: {len(info_items)}{RESET}")
    print(f"{YELLOW}Warnings: {len(warnings)}{RESET}")
    print(f"{BLOOD}Vulnerabilities: {len(vulnerabilities)}{RESET}")
    
    if vulnerabilities:
        print(f"\n{BLOOD}{BOLD}SECURITY RATING: CRITICAL - IMMEDIATE ACTION REQUIRED{RESET}")
    elif warnings:
        print(f"\n{YELLOW}{BOLD}SECURITY RATING: MODERATE - REVIEW RECOMMENDED{RESET}")
    else:
        print(f"\n{GREEN}{BOLD}SECURITY RATING: GOOD - NO MAJOR ISSUES FOUND{RESET}")
    
    save = input(f"\n{CYAN}Save detailed report? (y/n): {RESET}").strip().lower()
    if save == 'y':
        filename = f"security_scan_{domain.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump({
                'target': target_url,
                'domain': domain,
                'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'vulnerabilities': vulnerabilities,
                'warnings': warnings,
                'all_results': results
            }, f, indent=2)
        print(f"{GREEN}[+] Report saved: {filename}{RESET}")
    
    input(f"\n{GREEN}Press Enter to return...{RESET}")

def analyze_website_health():
    show_banner()
    print(f"{BRIGHT_RED}{BOLD}WEBSITE SECURITY HEALTH ANALYZER{RESET}")
    print(f"{WHITE}{'═'*80}{RESET}\n")

    target_url = input(f"{CYAN}Enter target URL: {RESET}").strip()
    if not target_url:
        print(f"{BLOOD}[ERROR] URL is required!{RESET}")
        input(f"{GREEN}Press Enter to return...{RESET}")
        return

    if not target_url.startswith('http'):
        target_url = 'https://' + target_url

    parsed = urlparse(target_url)
    domain = parsed.netloc

    print(f"\n{CYAN}[*] Analyzing: {target_url}{RESET}\n")

    report = {
        'target': target_url,
        'domain': domain,
        'scan_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'security_headers': {},
        'ssl_info': {},
        'server_info': {},
        'cors': {},
        'cookies': {},
        'risk_score': 0,
        'findings': []
    }

    risk_score = 0

    print(f"{BRIGHT_RED}[1] BASIC RESPONSE CHECK{RESET}")
    print(f"{WHITE}{'-'*60}{RESET}")
    try:
        resp = requests.get(target_url, timeout=10, verify=False, allow_redirects=True)
        status = resp.status_code
        print(f"{CYAN}Status Code:{RESET}     {GREEN}{status}{RESET}")
        print(f"{CYAN}Response Time:{RESET}   {resp.elapsed.total_seconds():.2f}s")
        print(f"{CYAN}Final URL:{RESET}       {resp.url}")
        print(f"{CYAN}Content-Type:{RESET}    {resp.headers.get('Content-Type', 'N/A')}")
        print(f"{CYAN}Content-Length:{RESET}  {len(resp.content)} bytes")
    except Exception as e:
        print(f"{BLOOD}[ERROR] Cannot reach target: {e}{RESET}")
        input(f"\n{GREEN}Press Enter to return...{RESET}")
        return

    print(f"\n{BRIGHT_RED}[2] SECURITY HEADERS ANALYSIS{RESET}")
    print(f"{WHITE}{'-'*60}{RESET}")

    security_headers = {
        'Strict-Transport-Security': {
            'desc': 'HSTS - Forces HTTPS',
            'severity': 'HIGH'
        },
        'Content-Security-Policy': {
            'desc': 'CSP - Prevents XSS/injection',
            'severity': 'HIGH'
        },
        'X-Frame-Options': {
            'desc': 'Clickjacking protection',
            'severity': 'MEDIUM'
        },
        'X-Content-Type-Options': {
            'desc': 'MIME-type sniffing protection',
            'severity': 'MEDIUM'
        },
        'Referrer-Policy': {
            'desc': 'Controls referrer info leakage',
            'severity': 'LOW'
        },
        'Permissions-Policy': {
            'desc': 'Controls browser feature access',
            'severity': 'LOW'
        },
        'X-XSS-Protection': {
            'desc': 'Legacy XSS filter (older browsers)',
            'severity': 'LOW'
        },
        'Cross-Origin-Embedder-Policy': {
            'desc': 'COEP - Cross-origin isolation',
            'severity': 'LOW'
        },
        'Cross-Origin-Opener-Policy': {
            'desc': 'COOP - Cross-origin isolation',
            'severity': 'LOW'
        },
    }

    missing_high = 0
    missing_medium = 0

    for header, meta in security_headers.items():
        value = resp.headers.get(header)
        if value:
            print(f"{GREEN}[✓] {header}{RESET}")
            print(f"    Value: {value[:60]}")
            report['security_headers'][header] = {'present': True, 'value': value}
        else:
            severity = meta['severity']
            color = BLOOD if severity == 'HIGH' else YELLOW if severity == 'MEDIUM' else WHITE
            print(f"{color}[✗] MISSING: {header} ({severity}){RESET}")
            print(f"    Info: {meta['desc']}")
            report['security_headers'][header] = {'present': False, 'severity': severity}
            report['findings'].append({
                'type': 'Missing Security Header',
                'item': header,
                'severity': severity,
                'description': meta['desc']
            })
            if severity == 'HIGH':
                missing_high += 1
                risk_score += 20
            elif severity == 'MEDIUM':
                missing_medium += 1
                risk_score += 10

    print(f"\n{BRIGHT_RED}[3] SERVER INFO LEAKAGE{RESET}")
    print(f"{WHITE}{'-'*60}{RESET}")

    leaky_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version',
                     'X-AspNetMvc-Version', 'X-Generator', 'X-Drupal-Cache']

    for lh in leaky_headers:
        val = resp.headers.get(lh)
        if val:
            print(f"{YELLOW}[!] {lh}: {val}{RESET}")
            report['server_info'][lh] = val
            report['findings'].append({
                'type': 'Information Leakage',
                'item': lh,
                'severity': 'LOW',
                'description': f'Server exposes: {val}'
            })
            risk_score += 5
        else:
            print(f"{GREEN}[✓] {lh}: Not exposed{RESET}")

    print(f"\n{BRIGHT_RED}[4] HTTPS / SSL CHECK{RESET}")
    print(f"{WHITE}{'-'*60}{RESET}")

    if parsed.scheme == 'https':
        print(f"{GREEN}[✓] Site uses HTTPS{RESET}")

        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    ssl_version = ssock.version()

                    print(f"{CYAN}SSL Version:{RESET}    {GREEN}{ssl_version}{RESET}")

                    subject = dict(x[0] for x in cert['subject'])
                    issuer = dict(x[0] for x in cert['issuer'])
                    not_after = cert.get('notAfter', 'Unknown')

                    print(f"{CYAN}Issued To:{RESET}      {subject.get('commonName', 'N/A')}")
                    print(f"{CYAN}Issued By:{RESET}      {issuer.get('organizationName', 'N/A')}")
                    print(f"{CYAN}Expires:{RESET}        {not_after}")

                    report['ssl_info'] = {
                        'version': ssl_version,
                        'subject': subject,
                        'issuer': issuer,
                        'expires': not_after
                    }

        except ssl.SSLError as e:
            print(f"{BLOOD}[!] SSL Error: {e}{RESET}")
            report['findings'].append({
                'type': 'SSL Issue',
                'item': 'SSL Certificate',
                'severity': 'HIGH',
                'description': str(e)
            })
            risk_score += 30

        hsts = resp.headers.get('Strict-Transport-Security')
        if not hsts:
            print(f"{YELLOW}[!] HSTS not enabled — HTTP downgrade possible{RESET}")
        else:
            print(f"{GREEN}[✓] HSTS enabled{RESET}")

        try:
            http_url = target_url.replace('https://', 'http://')
            http_resp = requests.get(http_url, timeout=5, verify=False, allow_redirects=False)
            if http_resp.status_code in [301, 302]:
                location = http_resp.headers.get('Location', '')
                if 'https' in location:
                    print(f"{GREEN}[✓] HTTP → HTTPS redirect in place{RESET}")
                else:
                    print(f"{YELLOW}[!] HTTP redirect does not force HTTPS{RESET}")
                    risk_score += 10
            else:
                print(f"{YELLOW}[!] HTTP version accessible without redirect (Status: {http_resp.status_code}){RESET}")
                risk_score += 15
        except:
            pass

    else:
        print(f"{BLOOD}[✗] Site does NOT use HTTPS — CRITICAL RISK{RESET}")
        report['findings'].append({
            'type': 'No HTTPS',
            'item': 'SSL/TLS',
            'severity': 'CRITICAL',
            'description': 'Website is served over plain HTTP'
        })
        risk_score += 50

    print(f"\n{BRIGHT_RED}[5] CORS CONFIGURATION{RESET}")
    print(f"{WHITE}{'-'*60}{RESET}")

    try:
        cors_resp = requests.get(
            target_url,
            headers={'Origin': 'https://evil-test-origin.com'},
            timeout=5,
            verify=False
        )
        acao = cors_resp.headers.get('Access-Control-Allow-Origin', '')
        acac = cors_resp.headers.get('Access-Control-Allow-Credentials', '')

        if acao == '*':
            print(f"{YELLOW}[!] CORS allows all origins (*){RESET}")
            report['cors']['allow_origin'] = acao
            report['findings'].append({
                'type': 'CORS Misconfiguration',
                'item': 'Access-Control-Allow-Origin: *',
                'severity': 'MEDIUM',
                'description': 'Wildcard CORS may expose API to unauthorized cross-origin access'
            })
            risk_score += 15
        elif 'evil-test-origin.com' in acao:
            print(f"{BLOOD}[!] CORS reflects arbitrary origins — HIGH RISK{RESET}")
            report['findings'].append({
                'type': 'CORS Misconfiguration',
                'item': 'Reflects arbitrary Origin',
                'severity': 'HIGH',
                'description': 'Server reflects any Origin header — vulnerable to CORS abuse'
            })
            risk_score += 25
        elif acao:
            print(f"{GREEN}[✓] CORS restricted to: {acao}{RESET}")
        else:
            print(f"{GREEN}[✓] No CORS headers (restricted){RESET}")

        if acac.lower() == 'true' and acao == '*':
            print(f"{BLOOD}[!] ACAO: * with Allow-Credentials: true — CRITICAL{RESET}")
            risk_score += 20

    except Exception as e:
        print(f"{BLOOD}[ERROR] CORS check failed: {e}{RESET}")

    print(f"\n{BRIGHT_RED}[6] COOKIE SECURITY{RESET}")
    print(f"{WHITE}{'-'*60}{RESET}")

    cookies = resp.cookies
    if cookies:
        for cookie in cookies:
            issues = []
            if not cookie.secure:
                issues.append('Missing Secure flag')
                risk_score += 5
            if not cookie.has_nonstandard_attr('HttpOnly'):
                issues.append('Missing HttpOnly flag')
                risk_score += 5
            if not cookie.has_nonstandard_attr('SameSite'):
                issues.append('Missing SameSite attribute')
                risk_score += 3

            if issues:
                print(f"{YELLOW}[!] Cookie '{cookie.name}': {', '.join(issues)}{RESET}")
                report['cookies'][cookie.name] = {'issues': issues}
                report['findings'].append({
                    'type': 'Insecure Cookie',
                    'item': cookie.name,
                    'severity': 'MEDIUM',
                    'description': ', '.join(issues)
                })
            else:
                print(f"{GREEN}[✓] Cookie '{cookie.name}': Properly configured{RESET}")
    else:
        print(f"{WHITE}[—] No cookies detected{RESET}")

    risk_score = min(risk_score, 100)
    report['risk_score'] = risk_score

    print(f"\n{BRIGHT_RED}{'='*80}")
    print(f"SECURITY HEALTH REPORT SUMMARY")
    print(f"{'='*80}{RESET}\n")

    print(f"{CYAN}Target:{RESET}      {target_url}")
    print(f"{CYAN}Scanned:{RESET}     {report['scan_time']}")
    print(f"{CYAN}Findings:{RESET}    {len(report['findings'])}")

    if risk_score >= 70:
        rating_color = BLOOD
        rating = "CRITICAL — Immediate action needed"
    elif risk_score >= 40:
        rating_color = YELLOW
        rating = "MODERATE — Several issues to address"
    elif risk_score >= 15:
        rating_color = CYAN
        rating = "LOW RISK — Minor improvements recommended"
    else:
        rating_color = GREEN
        rating = "HEALTHY — Good security posture"

    print(f"\n{rating_color}{BOLD}RISK SCORE: {risk_score}/100{RESET}")
    print(f"{rating_color}{BOLD}RATING: {rating}{RESET}")

    if report['findings']:
        print(f"\n{BRIGHT_RED}TOP FINDINGS:{RESET}")
        sorted_findings = sorted(
            report['findings'],
            key=lambda x: {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}.get(x['severity'], 4)
        )
        for f in sorted_findings[:10]:
            sev_color = BLOOD if f['severity'] in ['CRITICAL', 'HIGH'] else YELLOW if f['severity'] == 'MEDIUM' else WHITE
            print(f"  {sev_color}[{f['severity']}]{RESET} {f['type']}: {f['item']}")

    save = input(f"\n{CYAN}Save detailed report? (y/n): {RESET}").strip().lower()
    if save == 'y':
        filename = f"health_report_{domain.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"{GREEN}[+] Report saved: {filename}{RESET}")

    input(f"\n{GREEN}Press Enter to return...{RESET}")

def main_menu():
    while True:
        show_banner()
        
        print(f"{BOLD}SELECT MODE:{RESET}\n")
        print(f"{CYAN}[1]{RESET} 🔴 Automated Scanner   - Direct URL scan with security analysis")
        print(f"{CYAN}[2]{RESET} 📡 Packet Sniffer      - Network Traffic Capture (Requires Root)")
        print(f"{CYAN}[3]{RESET} 📋 View Captured       - View Intercepted Requests")
        print(f"{CYAN}[4]{RESET} 🔁 Repeater            - Manual Request Testing")
        print(f"{CYAN}[5]{RESET} ⚡ Intruder            - Automated Fuzzing Attack")
        print(f"{CYAN}[6]{RESET} 💾 Export Data         - Save All Captured Requests")
        print(f"{CYAN}[7]{RESET} ❌ Exit                - Close BurpSuite\n")
        
        choice = input(f"{BRIGHT_RED}[SELECT] >> {RESET}").strip()
        
        if choice == '1':
            analyze_website_health()
        elif choice == '2':
            packet_sniffer_mode()
        elif choice == '3':
            view_captured_requests()
        elif choice == '4':
            repeater_mode()
        elif choice == '5':
            intruder_mode()
        elif choice == '6':
            export_all_requests()
        elif choice == '7':
            print(f"\n{BLOOD}[*] Shutting down BurpSuite...{RESET}")
            print(f"{GREEN}[+] Goodbye!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{BLOOD}[!] Invalid choice{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{BLOOD}[!] Interrupted by user{RESET}")
        print(f"{GREEN}[+] Shutting down...{RESET}\n")
        sys.exit(0)