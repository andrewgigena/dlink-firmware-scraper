#!/usr/bin/env python3
import zipfile
import rarfile
import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, unquote
import time
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import threading

class DLinkFirmwareScraper:
    def __init__(self, base_url: str, download_path: str, target_models: List[str], ignored_extensions: List[str], max_parallel_downloads: int = 128):
        self.base_url = base_url
        self.download_path = download_path
        self.target_models = target_models
        self.ignored_extensions = [ext.lower().strip('.') for ext in ignored_extensions]
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.firmware_paths: Set[str] = set()
        self.max_parallel_downloads = max_parallel_downloads
        self.executor = ThreadPoolExecutor(max_workers=self.max_parallel_downloads)
        self.download_queue = queue.Queue()  # Queue for download tasks
        self.queue_lock = threading.Lock()

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
        # Skip if the file already exists
        if os.path.exists(local_path):
            print(f"⏭️ Skipping: {local_path} (already exists)")
            return False
    
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

                # Try to unpack zip and rar files
                if local_path.endswith(('.zip', '.rar')):
                    self.unpack_file(local_path)

                print(f"✅ Downloaded: {local_path}")
                return True
            except Exception as e:
                print(f"❌ Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    return False
                time.sleep(2 ** attempt)

    def unpack_file(self, file_path: str) -> None:
        """Unpack zip and rar files"""
        if file_path.endswith('.zip'):
            try:
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(os.path.dirname(file_path))
                print(f"✅ Unpacked: {file_path}")
            except zipfile.BadZipFile:
                print(f"❌ Failed to unpack: {file_path} (invalid zip file)")
        elif file_path.endswith('.rar'):
            try:
                with rarfile.RarFile(file_path, 'r') as rar_ref:
                    rar_ref.extractall(os.path.dirname(file_path))
                print(f"✅ Unpacked: {file_path}")
            except rarfile.BadRarFile:
                print(f"❌ Failed to unpack: {file_path} (invalid rar file)")

    def process_model_directory(self, model_url: str):
        """Process a specific model directory"""
        soup = self.get_soup(model_url)
        if not soup:
            return

        # Find all submodel directories
        links = soup.find_all('a')
        tasks = []
        for link in links:
            href = link.get('href')
            if not href or href in ['/', '../', '?C=N;O=D', '?C=M;O=A', '?C=S;O=A', '?C=D;O=A']:
                continue

            submodel_url = urljoin(model_url, unquote(href))
            if href.endswith('/'):
                # Process submodel directory concurrently
                submodel_name = href.strip('/')
                print(f"👉 Queuing submodel: {submodel_name}")
                tasks.append(self.executor.submit(self.process_submodel_directory, submodel_url))

        # Wait for all submodel processing tasks to complete
        for task in as_completed(tasks):
            task.result()  # Ensure exceptions are raised if any

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
                self.firmware_paths.add(firmware_url)
                self.process_firmware_directory(firmware_url)

    def process_firmware_directory(self, directory_url: str, depth: int = 0, max_depth: int = 5):
        """Recursively process a directory to find and download firmware files"""
        if depth > max_depth:
            print(f"⚠️ Maximum depth reached at {directory_url}")
            return

        soup = self.get_soup(directory_url)
        if not soup:
            return

        links = soup.find_all('a')
        
        for link in links:
            href = link.get('href')
            if not href or href in ['/', '../', '?C=N;O=D', '?C=M;O=A', '?C=S;O=A', '?C=D;O=A']:
                continue

            # Avoid processing parent directories (infinitely recursive)
            if "Parent Directory" in link:
                continue

            full_url = urljoin(directory_url, unquote(href))
            
            if href.endswith('/'):
                # It's a subdirectory - process it recursively
                self.process_firmware_directory(full_url, depth + 1, max_depth)
            else:
                # It's a file - check if we should download it
                if not self.should_download_file(href):
                    print(f"⏭️ Skipping ignored file type: {href}")
                    continue
                
                relative_path = full_url.replace(self.base_url, '').strip('/')
                local_path = os.path.join(self.download_path, relative_path)

                # Create any missing directories and subdirectories
                os.makedirs(os.path.dirname(local_path), exist_ok=True)

                # Add the download task to the queue
                self.download_queue.put((full_url, local_path))

        # Start worker threads to process the queue
        self.start_download_workers()

    def start_download_workers(self):
        """Start worker threads to process the download queue"""
        def worker():
            while True:
                try:
                    url, local_path = self.download_queue.get(timeout=5)  # Wait for tasks with a timeout
                    self.download_file(url, local_path)
                    self.download_queue.task_done()
                except queue.Empty:
                    break

        # Start multiple threads to download files concurrently
        threads = []
        for _ in range(self.max_parallel_downloads):
            thread = threading.Thread(target=worker)
            thread.start()
            threads.append(thread)

        # Wait for all threads to finish
        for thread in threads:
            thread.join()

    def run(self):
        """Main execution method"""
        print("\n=== D-Link Firmware Scraper ===")
        print(f"Base URL: {self.base_url}")
        print(f"Target Models: {', '.join(self.target_models)}")
        print(f"Download Path: {self.download_path}")
        print(f"Ignored Extensions: {', '.join(self.ignored_extensions)}")
        print("="*30)

        os.makedirs(self.download_path, exist_ok=True)

        tasks = []
        for model in self.target_models:
            model_url = urljoin(self.base_url, f"{model}/")
            print(f"👉 Queuing model: {model}")
            tasks.append(self.executor.submit(self.process_model_directory, model_url))

        # Wait for all model processing tasks to complete
        for task in as_completed(tasks):
            task.result()  # Ensure exceptions are raised if any

        # Wait for all download tasks to finish
        self.download_queue.join()

        print("\n=== Summary ===")
        print(f"Found {len(self.firmware_paths)} firmware directories:")
        for path in sorted(self.firmware_paths):
            print(f"📁 {path}")

if __name__ == "__main__":
    BASE_URL = "http://downloads.d-link.co.za/"
    DOWNLOAD_PATH = "dlink_firmware"
    TARGET_MODELS = ["DAP", "DIR", "DRA", "E", "G", "M", "R"]
    IGNORED_EXTENSIONS = ['doc', 'pdf', 'txt', 'xls', 'docx', 'md5']
    
    scraper = DLinkFirmwareScraper(BASE_URL, DOWNLOAD_PATH, TARGET_MODELS, IGNORED_EXTENSIONS)
    scraper.run()
