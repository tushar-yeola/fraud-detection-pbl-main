"""Capture screenshots of all FraudShield pages using Selenium."""
import time
import sys
import io
import os

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

BASE_URL = "http://localhost:5174"
SCREENSHOTS_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

opts = Options()
opts.add_argument("--start-maximized")
opts.add_argument("--disable-notifications")
opts.add_argument("--force-device-scale-factor=1")

try:
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=opts
    )
except Exception:
    driver = webdriver.Chrome(options=opts)

driver.implicitly_wait(8)
driver.set_window_size(1400, 900)

pages = [
    ("/", "01_dashboard.png"),
    ("/check", "02_check_transaction.png"),
    ("/transactions", "03_transactions.png"),
    ("/alerts", "04_fraud_alerts.png"),
    ("/analytics", "05_analytics.png"),
    ("/model", "06_model_info.png"),
]

for path, filename in pages:
    url = BASE_URL + path
    print(f"Capturing {url} -> {filename}")
    driver.get(url)
    time.sleep(3)
    filepath = os.path.join(SCREENSHOTS_DIR, filename)
    driver.save_screenshot(filepath)
    print(f"  Saved: {filepath}")

print("\nAll screenshots captured!")
driver.quit()
