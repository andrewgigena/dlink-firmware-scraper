
# D-Link Firmware Scraper

A Python scraper designed to download firmware files for specific D-Link models from the official D-Link website. This tool allows you to collect and store firmware files, excluding certain file types based on your preferences.

## Features

- Scrapes D-Link firmware directories for multiple models.
- Skips downloading unwanted file types (e.g., `.pdf`, `.txt`, `.docx`).
- Provides retry logic for downloading firmware files.
- Supports easy configuration for model selection and file exclusion.
- Outputs a summary of found firmware directories.

## Requirements

- Python 3.x
- Poetry (for dependency management)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/dlink-firmware-scraper.git
cd dlink-firmware-scraper
```

2. Install Poetry (if you don't have it installed):

Follow the installation instructions from the [Poetry documentation](https://python-poetry.org/docs/#installation).

3. Install project dependencies:

```bash
poetry install
```

This will install the required dependencies listed in the `pyproject.toml` file.

## Configuration

Modify the script configuration to suit your needs:

- `BASE_URL`: The base URL for the D-Link firmware repository.
- `DOWNLOAD_PATH`: The local path where firmware files will be saved.
- `TARGET_MODELS`: List of models to scrape (e.g., `["DAP", "DIR", "DRA"]`).
- `IGNORED_EXTENSIONS`: List of file extensions to exclude from downloads (e.g., `["pdf", "txt", "md5"]`).

## Usage

Run the scraper with Poetry:

```bash
poetry run python scraper.py
```

The script will process the target models and download the firmware files to the specified download path.

## Example Output

```
=== D-Link Firmware Scraper ===
Base URL: http://downloads.d-link.co.za/
Target Models: DAP, DIR, DRA
Download Path: dlink_firmware
Ignored Extensions: doc, pdf, txt, xls, docx, md5
==============================

👉 Processing model: DAP
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1150/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1155/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1160/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1320/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1325/firmware/
✅ Downloaded: dlink_firmware/DAP/dap1325/firmware/DAP-1325A1_FW102b04 (Middle FW).bin
✅ Downloaded: dlink_firmware/DAP/dap1325/firmware/DAP-1325A1_FW106B06.bin
⏭ Skipping ignored file type: DAP-1325_A1_FW1.02_Release%20Notes.pdf
⏭ Skipping ignored file type: DAP-1325_A1_FW1.06_Release%20Notes.doc
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1330/Firmware/
⏭ Skipping ignored file type: DAP-1330A1_FWv101_Release%20Notes.pdf
✅ Downloaded: dlink_firmware/DAP/dap1330/Firmware/DAP1330A1_FW101B03.bin
✅ Downloaded: dlink_firmware/DAP/dap1330/Firmware/DAP1330A1_FW101B04.bin
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1350/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1353/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1360/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1520/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1522/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1525/Firmware/
✅ Downloaded: dlink_firmware/DAP/dap1525/Firmware/DAP1525B1_FW200B23.bin
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1530/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1560/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1610/firmware/
✅ Downloaded: dlink_firmware/DAP/dap1610/firmware/DAP-1610_A2_FW_1.05b01.bin
✅ Downloaded: dlink_firmware/DAP/dap1610/firmware/DAP-1610_A2_FW_1.08b01.bin
⏭ Skipping ignored file type: DAP-1610_A2_FW_v1.05_Release%20Notes.pdf
⏭ Skipping ignored file type: DAP-1610_A2_FW_v1.08_Release_Notes.pdf
✅ Downloaded: dlink_firmware/DAP/dap1610/firmware/DAP-1610_FW_1.07b_HQ.bin
✅ Downloaded: dlink_firmware/DAP/dap1610/firmware/DAP_1610_A2_3.0.1_RS.bin
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1620/Firmware/
✅ Downloaded: dlink_firmware/DAP/dap1620/Firmware/DAP1620A1_A2_FW105B05.bin
✅ Downloaded: dlink_firmware/DAP/dap1620/Firmware/DAP1620A1_FW104B04.bin
❌ Attempt 1 failed for http://downloads.d-link.co.za/DAP/dap1620/Firmware/DAP1620A1_FW106b04Beta01(0927093853).7z: ('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))
✅ Downloaded: dlink_firmware/DAP/dap1620/Firmware/DAP1620A1_FW106b04Beta01(0927093853).7z
✅ Downloaded: dlink_firmware/DAP/dap1620/Firmware/DAP1620A1_FW106b04Beta03(1018174458)(1019105835).7z
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1650/Firmware/
✅ Downloaded: dlink_firmware/DAP/dap1650/Firmware/DAP1650_FW103WWb07.bin
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1665/Firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1720/firmware/
📁 Found firmware directory: http://downloads.d-link.co.za/DAP/dap1860/Firmware/
```

## Contributing

Feel free to fork the repository, create issues, and submit pull requests. Contributions are always welcome!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
