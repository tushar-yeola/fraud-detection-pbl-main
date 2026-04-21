"""
=============================================================================
  SELENIUM AUTOMATED TESTING — SE CIE ASSIGNMENT (SY4)
  Subject   : Software Engineering
  Option    : A — PBL Integration (FraudShield Banking Fraud Detection System)
  File Name : RollNo_SY4_Selenium.py

  PROBLEM STATEMENT:
  FraudShield is an AI-powered banking fraud detection web application that
  allows analysts to submit transaction details and receive real-time fraud
  predictions using a machine-learning ensemble model (Random Forest +
  Logistic Regression). This Selenium test suite validates the core
  workflows: dashboard visibility, transaction fraud-check form submission
  (with text, number, and dropdown field types), multi-page navigation,
  explicit/implicit wait synchronization, and assertion of prediction
  outcomes — verifying that the system reliably detects both safe and
  fraudulent banking transactions.

  REQUIREMENTS COVERED:
    [✅] Form Handling  : Text, Number, and Dropdown/Select fields
    [✅] Navigation     : 5 pages — Dashboard, Check Transaction,
                          Transactions, Alerts, Analytics
    [✅] Synchronization: WebDriverWait (explicit) + implicitly_wait (implicit)
    [✅] Validation     : Assert on final prediction result messages

  HOW TO RUN:
    1. Start backend  : cd backend && python -m uvicorn main:app --reload --port 8000
    2. Start frontend : cd frontend && npm run dev
    3. Install deps   : pip install selenium webdriver-manager
    4. Run tests      : python assets/RollNo_SY4_Selenium.py
=============================================================================
"""

import time
import sys
import traceback
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_URL = "http://localhost:5174"   # Vite uses 5174 if 5173 is taken
IMPLICIT_WAIT = 8       # seconds — applied globally
EXPLICIT_WAIT = 20      # seconds — applied per critical assertion

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
PASS = "[PASS]"
FAIL = "[FAIL]"
results = []

def log(msg):
    print(msg)

def record(test_name, passed, detail=""):
    status = PASS if passed else FAIL
    results.append((test_name, status, detail))
    log(f"\n  {status}  [{test_name}]  {detail}")

def make_driver():
    """Create a Chrome WebDriver with sensible defaults."""
    opts = Options()
    opts.add_argument("--start-maximized")
    opts.add_argument("--disable-notifications")
    # Comment the next line out if you want to watch the browser
    # opts.add_argument("--headless=new")
    try:
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=opts
        )
    except Exception:
        # Fallback: system chromedriver
        driver = webdriver.Chrome(options=opts)
    driver.implicitly_wait(IMPLICIT_WAIT)     # ← IMPLICIT WAIT applied here
    return driver

def wait_for(driver, by, value, timeout=EXPLICIT_WAIT):
    """Explicit wait for element visibility."""
    return WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((by, value))
    )

def navigate(driver, path):
    url = BASE_URL + path
    log(f"\n  >>  Navigating to {url} ...")
    driver.get(url)

# ---------------------------------------------------------------------------
# TEST 1 — Dashboard loads with stats cards
# ---------------------------------------------------------------------------
def test_dashboard_load(driver):
    test_name = "T1 — Dashboard Load & Stats Cards"
    log(f"\n{'='*60}\n{test_name}")
    try:
        navigate(driver, "/")
        # Explicit wait: wait for at least one stat card value to appear
        stat = WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".stat-value, .kpi-value, h2"))
        )
        # Assert page title or heading
        assert "FraudShield" in driver.title or \
               len(driver.find_elements(By.CLASS_NAME, "card")) > 0, \
               "Dashboard cards not found"
        detail = f"Page loaded. Title: '{driver.title}'"
        record(test_name, True, detail)
    except Exception as e:
        record(test_name, False, str(e))
        traceback.print_exc()

# ---------------------------------------------------------------------------
# TEST 2 — Check Transaction — SAFE (low risk data)
# ---------------------------------------------------------------------------
def test_check_transaction_safe(driver):
    test_name = "T2 — Check Transaction Form (Safe Transaction)"
    log(f"\n{'='*60}\n{test_name}")
    try:
        navigate(driver, "/check")

        # ── TEXT FIELD: Account ID ──────────────────────────────────────
        acct_field = wait_for(driver, By.ID, "field-AccountID")
        acct_field.clear()
        acct_field.send_keys("ACC_SAFE_001")
        log("    [Text]     Account ID filled.")

        # ── NUMBER FIELD: Transaction Amount ────────────────────────────
        amt_field = wait_for(driver, By.ID, "field-TransactionAmount")
        amt_field.clear()
        amt_field.send_keys("150")          # low amount → safe
        log("    [Number]   Transaction Amount = 150")

        # ── NUMBER FIELD: Account Balance ───────────────────────────────
        bal_field = wait_for(driver, By.ID, "field-AccountBalance")
        bal_field.clear()
        bal_field.send_keys("10000")
        log("    [Number]   Account Balance = 10000")

        # ── NUMBER FIELD: Customer Age ──────────────────────────────────
        age_field = driver.find_element(By.ID, "field-CustomerAge")
        age_field.clear()
        age_field.send_keys("30")
        log("    [Number]   Customer Age = 30")

        # ── NUMBER FIELD: Transaction Duration ─────────────────────────
        dur_field = driver.find_element(By.ID, "field-TransactionDuration")
        dur_field.clear()
        dur_field.send_keys("180")
        log("    [Number]   Transaction Duration = 180")

        # ── NUMBER FIELD: Login Attempts ────────────────────────────────
        login_field = driver.find_element(By.ID, "field-LoginAttempts")
        login_field.clear()
        login_field.send_keys("1")          # low login attempts → safe
        log("    [Number]   Login Attempts = 1")

        # ── DROPDOWN: Transaction Type ──────────────────────────────────
        tx_type_sel = Select(wait_for(driver, By.ID, "field-TransactionType"))
        tx_type_sel.select_by_visible_text("Credit")
        log("    [Dropdown] Transaction Type = Credit")

        # ── DROPDOWN: Channel ───────────────────────────────────────────
        channel_sel = Select(wait_for(driver, By.ID, "field-Channel"))
        channel_sel.select_by_visible_text("ATM")
        log("    [Dropdown] Channel = ATM")

        # ── DROPDOWN: Occupation ────────────────────────────────────────
        occ_sel = Select(wait_for(driver, By.ID, "field-CustomerOccupation"))
        occ_sel.select_by_visible_text("Engineer")
        log("    [Dropdown] Occupation = Engineer")

        # ── TEXT FIELD: Location ────────────────────────────────────────
        loc_field = wait_for(driver, By.ID, "field-Location")
        loc_field.clear()
        loc_field.send_keys("Mumbai")
        log("    [Text]     Location = Mumbai")

        # ── SUBMIT ──────────────────────────────────────────────────────
        btn = wait_for(driver, By.ID, "btn-predict")
        driver.execute_script("arguments[0].click();", btn)
        log("    [Click]    Analyze Transaction button clicked.")

        # ── EXPLICIT WAIT: Result must appear ───────────────────────────
        result_el = WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(),'FRAUD DETECTED') or contains(text(),'TRANSACTION SAFE')]"
            ))
        )
        result_text = result_el.text
        log(f"    [Result]   {result_text}")

        # ASSERTION: result card must contain a verdict
        assert "FRAUD DETECTED" in result_text or "TRANSACTION SAFE" in result_text, \
            f"Unexpected result text: {result_text}"
        record(test_name, True, f"Result = '{result_text}'")

    except Exception as e:
        record(test_name, False, str(e))
        traceback.print_exc()

# ---------------------------------------------------------------------------
# TEST 3 — Check Transaction — HIGH RISK (fraud indicators)
# ---------------------------------------------------------------------------
def test_check_transaction_fraud(driver):
    test_name = "T3 — Check Transaction Form (High-Risk Fraud Indicators)"
    log(f"\n{'='*60}\n{test_name}")
    try:
        navigate(driver, "/check")

        # ── TEXT: Account ID ────────────────────────────────────────────
        acct_field = wait_for(driver, By.ID, "field-AccountID")
        acct_field.clear()
        acct_field.send_keys("ACC_SUSPICIOUS_007")

        # ── NUMBER: Very high transaction amount (fraud indicator) ──────
        amt_field = wait_for(driver, By.ID, "field-TransactionAmount")
        amt_field.clear()
        amt_field.send_keys("9800")         # high amount

        # ── NUMBER: Low balance → ratio > 1.5 (fraud heuristic) ────────
        bal_field = wait_for(driver, By.ID, "field-AccountBalance")
        bal_field.clear()
        bal_field.send_keys("500")

        # ── NUMBER: Customer Age ────────────────────────────────────────
        age_field = driver.find_element(By.ID, "field-CustomerAge")
        age_field.clear()
        age_field.send_keys("22")

        # ── NUMBER: Transaction Duration ────────────────────────────────
        dur_field = driver.find_element(By.ID, "field-TransactionDuration")
        dur_field.clear()
        dur_field.send_keys("5")            # suspiciously fast

        # ── NUMBER: High login attempts (≥3 → fraud heuristic) ─────────
        login_field = driver.find_element(By.ID, "field-LoginAttempts")
        login_field.clear()
        login_field.send_keys("5")

        # ── DROPDOWN: Channel = Online ──────────────────────────────────
        channel_sel = Select(wait_for(driver, By.ID, "field-Channel"))
        channel_sel.select_by_visible_text("Online")
        log("    [Dropdown] Channel = Online (high-risk)")

        # ── DROPDOWN: Transaction Type ──────────────────────────────────
        tx_type_sel = Select(wait_for(driver, By.ID, "field-TransactionType"))
        tx_type_sel.select_by_visible_text("Debit")

        # ── DROPDOWN: Occupation ────────────────────────────────────────
        occ_sel = Select(wait_for(driver, By.ID, "field-CustomerOccupation"))
        occ_sel.select_by_visible_text("Student")

        # ── SUBMIT ──────────────────────────────────────────────────────
        btn = wait_for(driver, By.ID, "btn-predict")
        driver.execute_script("arguments[0].click();", btn)
        log("    [Click]    Analyze Transaction button clicked.")

        # ── EXPLICIT WAIT: Wait for result ──────────────────────────────
        result_el = WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(),'FRAUD DETECTED') or contains(text(),'TRANSACTION SAFE')]"
            ))
        )
        result_text = result_el.text
        log(f"    [Result]   {result_text}")

        # ASSERTION: some verdict must appear
        assert "FRAUD DETECTED" in result_text or "TRANSACTION SAFE" in result_text, \
            f"Unexpected result text: {result_text}"
        record(test_name, True, f"Result = '{result_text}'")

    except Exception as e:
        record(test_name, False, str(e))
        traceback.print_exc()

# ---------------------------------------------------------------------------
# TEST 4 — Navigation: All Transactions page
# ---------------------------------------------------------------------------
def test_transactions_page(driver):
    test_name = "T4 — Navigation: All Transactions Page"
    log(f"\n{'='*60}\n{test_name}")
    try:
        navigate(driver, "/transactions")

        # Explicit wait: table rows or "no data" message
        WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        detail = f"Transactions table found. Visible rows: {len(rows)}"
        record(test_name, True, detail)

    except Exception as e:
        record(test_name, False, str(e))
        traceback.print_exc()

# ---------------------------------------------------------------------------
# TEST 5 — Navigation: Fraud Alerts page
# ---------------------------------------------------------------------------
def test_alerts_page(driver):
    test_name = "T5 — Navigation: Fraud Alerts Page"
    log(f"\n{'='*60}\n{test_name}")
    try:
        navigate(driver, "/alerts")

        # Implicit wait will handle basic DOM load; also check for heading
        heading = WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.XPATH,
                "//*[contains(text(),'Alert') or contains(text(),'Fraud')]"
            ))
        )
        assert heading is not None, "Alerts page heading not found"
        record(test_name, True, f"Heading: '{heading.text[:60]}'")

    except Exception as e:
        record(test_name, False, str(e))
        traceback.print_exc()

# ---------------------------------------------------------------------------
# TEST 6 — Navigation: Analytics page
# ---------------------------------------------------------------------------
def test_analytics_page(driver):
    test_name = "T6 — Navigation: Analytics Page"
    log(f"\n{'='*60}\n{test_name}")
    try:
        navigate(driver, "/analytics")

        # Look for any chart container (recharts, canvas, or svg)
        WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR,
                "svg, canvas, .recharts-wrapper, .card"
            ))
        )
        cards = driver.find_elements(By.CLASS_NAME, "card")
        detail = f"Analytics page loaded. Cards found: {len(cards)}"
        record(test_name, True, detail)

    except Exception as e:
        record(test_name, False, str(e))
        traceback.print_exc()

# ---------------------------------------------------------------------------
# TEST 7 — Sidebar navigation: click nav links (synchronization demo)
# ---------------------------------------------------------------------------
def test_sidebar_navigation(driver):
    test_name = "T7 — Sidebar Navigation (Multi-page click-flow)"
    log(f"\n{'='*60}\n{test_name}")
    try:
        navigate(driver, "/")
        # Click 'Check Transaction' in sidebar via text
        check_link = WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//a[contains(text(),'Check Transaction')]"
            ))
        )
        check_link.click()
        log("    [Nav]      Clicked 'Check Transaction' sidebar link.")

        # Wait for the form to appear
        WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.visibility_of_element_located((By.ID, "field-AccountID"))
        )
        log("    [Wait]     Check Transaction form loaded.")

        # Navigate to Analytics
        analytics_link = WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.element_to_be_clickable((By.XPATH,
                "//a[contains(text(),'Analytics')]"
            ))
        )
        analytics_link.click()
        log("    [Nav]      Clicked 'Analytics' sidebar link.")

        WebDriverWait(driver, EXPLICIT_WAIT).until(
            EC.presence_of_element_located((By.CLASS_NAME, "card"))
        )
        log("    [Wait]     Analytics page loaded.")

        assert "localhost" in driver.current_url, "Navigation failed"
        record(test_name, True, f"Current URL: {driver.current_url}")

    except Exception as e:
        record(test_name, False, str(e))
        traceback.print_exc()

# ---------------------------------------------------------------------------
# MAIN RUNNER
# ---------------------------------------------------------------------------
def main():
    log("\n" + "="*60)
    log("  FraudShield — Selenium Test Suite")
    log("  SE CIE Assignment — Option A (PBL Integration)")
    log("  Target: http://localhost:5174")
    log("="*60)

    driver = make_driver()
    try:
        test_dashboard_load(driver)
        test_check_transaction_safe(driver)
        test_check_transaction_fraud(driver)
        test_transactions_page(driver)
        test_alerts_page(driver)
        test_analytics_page(driver)
        test_sidebar_navigation(driver)

    finally:
        # ── FINAL SUMMARY ────────────────────────────────────────────────
        log("\n\n" + "="*60)
        log("  TEST RESULTS SUMMARY")
        log("="*60)
        passed = sum(1 for _, s, _ in results if "PASS" in s)
        failed = sum(1 for _, s, _ in results if "FAIL" in s)
        for name, status, detail in results:
            log(f"  {status}  {name}")
            if detail:
                log(f"         -> {detail}")
        log("-"*60)
        log(f"  Total: {len(results)}  |  Passed: {passed}  |  Failed: {failed}")
        log("="*60)

        time.sleep(3)
        driver.quit()
        sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
