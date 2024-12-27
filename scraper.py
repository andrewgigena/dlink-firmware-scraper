import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, unquote
import time
from typing import Set, List

class DLinkFirmwareScraper:
    def __init__(self, base_url: str, download_path: str, target_models: List[str], ignored_extensions: List[str]):
        self.base_url = base_url
        self.download_path = download_path
        self.target_models = target_models
        self.ignored_extensions = [ext.lower().strip('.') for ext in ignored_extensions]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.firmware_paths: Set[str] = set()

    def should_download_file(self, filename: str) -> bool:
        """Check if the file should be downloaded based on its extension"""
        file_extension = os.path.splitext(filename.lower())[1].strip('.')
        return file_extension not in self.ignored_extensions

    def get_soup(self, url: str) -> BeautifulSoup:
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            print(f"Error accessing {url}: {str(e)}")
            return None

    def download_file(self, url: str, local_path: str) -> bool:
        """Download a single file with retry logic"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                print(f"✅ Downloaded: {local_path}")
                return True
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(2 ** attempt)

    def process_model_directory(self, model_url: str):
        """Process a specific model directory"""
        soup = self.get_soup(model_url)
        if not soup:
            return

        # Find all submodel directories
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if not href or href in ['/', '../', '?C=N;O=D', '?C=M;O=A', '?C=S;O=A', '?C=D;O=A']:
                continue

            submodel_url = urljoin(model_url, unquote(href))
            if href.endswith('/'):
                # Process submodel directory
                self.process_submodel_directory(submodel_url)

    def process_submodel_directory(self, submodel_url: str):
        """Process a submodel directory to find firmware folders"""
        soup = self.get_soup(submodel_url)
        if not soup:
            return

        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if not href or href in ['/', '../', '?C=N;O=D', '?C=M;O=A', '?C=S;O=A', '?C=D;O=A']:
                continue

            if href.lower() in ['firmware/', 'Firmware/']:
                firmware_url = urljoin(submodel_url, unquote(href))
                print(f"📁 Found firmware directory: {firmware_url}")
                self.firmware_paths.add(firmware_url)
                self.download_firmware_files(firmware_url)

    def download_firmware_files(self, firmware_url: str):
        """Download all files from a firmware directory"""
        soup = self.get_soup(firmware_url)
        if not soup:
            return

        links = soup.find_all('a')
        for link in links:
            href = link.get('href')
            if not href or href in ['/', '../', '?C=N;O=D', '?C=M;O=A', '?C=S;O=A', '?C=D;O=A']:
                continue

            if not href.endswith('/'):  # It's a file
                if not self.should_download_file(href):
                    print(f"⏭️ Skipping ignored file type: {href}")
                    continue
                    
                file_url = urljoin(firmware_url, unquote(href))
                relative_path = file_url.replace(self.base_url, '').strip('/')
                local_path = os.path.join(self.download_path, relative_path)
                self.download_file(file_url, local_path)

    def run(self):
        """Main execution method"""
        print("\n=== D-Link Firmware Scraper ===")
        print(f"Base URL: {self.base_url}")
        print(f"Target Models: {', '.join(self.target_models)}")
        print(f"Download Path: {self.download_path}")
        print(f"Ignored Extensions: {', '.join(self.ignored_extensions)}")
        print("="*30)

        os.makedirs(self.download_path, exist_ok=True)

        for model in self.target_models:
            model_url = urljoin(self.base_url, f"{model}/")
            print(f"\n👉 Processing model: {model}")
            self.process_model_directory(model_url)

        print("\n=== Summary ===")
        print(f"Found {len(self.firmware_paths)} firmware directories:")
        for path in sorted(self.firmware_paths):
            print(f"📁 {path}")

if __name__ == "__main__":
    BASE_URL = "http://downloads.d-link.co.za/"
    DOWNLOAD_PATH = "dlink_firmware"
    TARGET_MODELS = ["DAP", "DIR", "DRA"]
    IGNORED_EXTENSIONS = ['doc', 'pdf', 'txt', 'xls', 'docx', 'md5']
    
    scraper = DLinkFirmwareScraper(BASE_URL, DOWNLOAD_PATH, TARGET_MODELS, IGNORED_EXTENSIONS)
    scraper.run()