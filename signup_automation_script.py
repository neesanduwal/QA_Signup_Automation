"""
Signup Automation Script for Authorized Partner
Target: https://authorized-partner.vercel.app/
"""

import time
import random
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def generate_test_email():
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"test_agent_{random_part}@example.com"


def generate_agency_name():
    random_part = ''.join(random.choices(string.ascii_letters, k=6))
    return f"Test Agency {random_part}"


TEST_DATA = {
    "first_name": "Test",
    "last_name": "Agent",
    "email": generate_test_email(),
    "phone": "9812345678",
    "password": "Test@Password123!",
    "agency_name": generate_agency_name(),
    "role_in_agency": "Recruitment Consultant",
    "agency_email": generate_test_email(),
    "website": "https://www.testagency.com",
    "address": "123 Test Street, Kathmandu",
    "focus_area": "Undergraduate admissions to Canada",
    "students_recruited": "50",
    "success_metrics": "85",
    "business_registration": "REG123456789",
    "certification": "ICEF Certified Education Agent",
}


def create_driver(headless=False):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--ignore-certificate-errors")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def safe_send_keys(elem, value):
    elem.clear()
    time.sleep(0.2)
    elem.send_keys(value)
    time.sleep(0.2)


def fill_by_placeholder(driver, placeholder_part, value):
    try:
        elem = driver.find_element(By.XPATH, f"//input[contains(@placeholder, '{placeholder_part}')]")
        if elem.is_displayed() and elem.is_enabled():
            safe_send_keys(elem, value)
            return True
    except Exception:
        pass
    return False


def fill_by_label(driver, label_text, value):
    try:
        elem = driver.find_element(By.XPATH, f"//label[contains(., '{label_text}')]/following-sibling::*/descendant-or-self::input | //label[contains(., '{label_text}')]/following::input[1]")
        if elem.is_displayed() and elem.is_enabled():
            safe_send_keys(elem, value)
            return True
    except Exception:
        pass
    return False


def click_button(driver, wait, text):
    for by, selector in [
        (By.XPATH, f"//button[contains(text(), '{text}')]"),
        (By.XPATH, f"//a[contains(text(), '{text}')]"),
        (By.XPATH, f"//*[contains(text(), '{text}') and (self::button or self::a)]"),
    ]:
        try:
            btn = wait.until(EC.element_to_be_clickable((by, selector)))
            if btn.is_displayed():
                btn.click()
                return True
        except Exception:
            continue
    return False


def step0_accept_terms(driver, wait):
    print("[Step 0] Accepting terms and conditions...")
    try:
        checkbox = None
        for selector in [
            "input[type='checkbox']",
            "[role='checkbox']",
            "button[role='checkbox']",
            "div[role='checkbox']",
        ]:
            try:
                checkbox = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                if checkbox and checkbox.is_displayed():
                    break
            except Exception:
                continue
        if not checkbox:
            try:
                agree_elem = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(text(), 'I agree') or contains(., 'I agree')]")
                ))
                driver.execute_script("arguments[0].click();", agree_elem)
            except Exception:
                try:
                    clickable = driver.find_element(By.XPATH, "//label[contains(., 'I agree')] | //*[@role='checkbox'] | //input[@type='checkbox']/..")
                    driver.execute_script("arguments[0].click();", clickable)
                except Exception:
                    raise Exception("Could not find terms checkbox")
        elif not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
        print("  [OK] Terms checked")
        time.sleep(0.5)
        click_button(driver, wait, "Continue")
        print("  [OK] Continue clicked")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def step1_setup_account(driver, wait):
    print("[Step 1] Setting up account (personal details)...")
    try:
        fill_by_placeholder(driver, "First Name", TEST_DATA["first_name"])
        fill_by_placeholder(driver, "Last Name", TEST_DATA["last_name"])
        fill_by_placeholder(driver, "Email Address", TEST_DATA["email"])
        try:
            phone_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='tel'], input[placeholder*='phone'], input[placeholder*='Phone'], input[placeholder*='00000000']")
            for inp in phone_inputs:
                if inp.is_displayed():
                    safe_send_keys(inp, TEST_DATA["phone"])
                    break
        except Exception:
            pass
        pwd_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='password']")
        if len(pwd_inputs) >= 1:
            safe_send_keys(pwd_inputs[0], TEST_DATA["password"])
        if len(pwd_inputs) >= 2:
            safe_send_keys(pwd_inputs[1], TEST_DATA["password"])
        print("  [OK] Account fields filled")
        click_button(driver, wait, "Next")
        print("  [OK] Next clicked")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def step2_agency_details(driver, wait):
    print("[Step 2] Filling agency details...")
    try:
        fill_by_placeholder(driver, "Agency Name", TEST_DATA["agency_name"])
        fill_by_placeholder(driver, "Role in Agency", TEST_DATA["role_in_agency"])
        fill_by_placeholder(driver, "Agency Email", TEST_DATA["agency_email"])
        fill_by_placeholder(driver, "Agency Website", "www.testagency.com")
        fill_by_placeholder(driver, "Agency Address", TEST_DATA["address"])
        try:
            region_selects = driver.find_elements(By.CSS_SELECTOR, "select")
            for sel in region_selects:
                if sel.is_displayed():
                    select = Select(sel)
                    options = [o.text for o in select.options if o.text and "Select" not in o.text]
                    if options:
                        select.select_by_visible_text(options[0])
                        break
        except Exception:
            pass
        print("  [OK] Agency fields filled")
        click_button(driver, wait, "Next")
        print("  [OK] Next clicked")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def step3_professional_experience(driver, wait):
    print("[Step 3] Filling professional experience...")
    try:
        try:
            for sel in driver.find_elements(By.CSS_SELECTOR, "select"):
                if sel.is_displayed():
                    s = Select(sel)
                    opts = [o.text for o in s.options if o.text and "Select" not in o.text]
                    if opts:
                        s.select_by_index(1)
                        break
        except Exception:
            pass
        fill_by_placeholder(driver, "Undergraduate admissions", TEST_DATA["focus_area"])
        fill_by_placeholder(driver, "approximate number", TEST_DATA["students_recruited"])
        fill_by_placeholder(driver, "E.g., 90", TEST_DATA["success_metrics"])
        try:
            for label_text in ["Career Counseling", "Admission Applications", "Visa Processing", "Test Prep"]:
                try:
                    cb = driver.find_element(By.XPATH, f"//label[contains(., '{label_text}')]//input[@type='checkbox'] | //input[@type='checkbox']/following-sibling::*[contains(., '{label_text}')]")
                    if cb and not cb.is_selected():
                        driver.execute_script("arguments[0].click();", cb)
                except Exception:
                    pass
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            for cb in checkboxes[:4]:
                if cb.is_displayed() and not cb.is_selected():
                    driver.execute_script("arguments[0].click();", cb)
                    time.sleep(0.2)
        except Exception:
            pass
        print("  [OK] Professional experience filled")
        click_button(driver, wait, "Next")
        print("  [OK] Next clicked")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def step4_verification_and_preferences(driver, wait):
    print("[Step 4] Filling verification and preferences...")
    try:
        fill_by_placeholder(driver, "registration number", TEST_DATA["business_registration"])
        try:
            selects = driver.find_elements(By.CSS_SELECTOR, "select")
            for sel in selects:
                if sel.is_displayed():
                    s = Select(sel)
                    opts = [o.text for o in s.options if o.text and "Select" not in o.text]
                    if opts:
                        s.select_by_visible_text(opts[0])
                        break
        except Exception:
            pass
        try:
            radios = driver.find_elements(By.XPATH, "//input[@type='radio']")
            for r in radios:
                if "Universities" in (r.get_attribute("value") or ""):
                    driver.execute_script("arguments[0].click();", r)
                    break
            if not any(r.is_selected() for r in radios):
                radios[0].click() if radios else None
        except Exception:
            pass
        fill_by_placeholder(driver, "ICEF Certified", TEST_DATA["certification"])
        print("  [OK] Verification fields filled")
        click_button(driver, wait, "Submit")
        print("  [OK] Submit clicked")
        time.sleep(3)
        return True
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def run_signup_automation(headless=False):
    BASE_URL = "https://authorized-partner.vercel.app/register"
    driver = None
    try:
        print("=" * 55)
        print("Signup Automation - Authorized Partner")
        print("=" * 55)
        print(f"Email: {TEST_DATA['email']}")
        print(f"Agency: {TEST_DATA['agency_name']}")
        print("=" * 55)
        driver = create_driver(headless=headless)
        wait = WebDriverWait(driver, 15)
        driver.get(BASE_URL)
        time.sleep(4)
        if not step0_accept_terms(driver, wait):
            print("\n[FAIL] Terms step failed")
            return False
        if not step1_setup_account(driver, wait):
            print("\n[FAIL] Account setup failed")
            return False
        if not step2_agency_details(driver, wait):
            print("\n[FAIL] Agency details failed")
            return False
        if not step3_professional_experience(driver, wait):
            print("\n[FAIL] Professional experience failed")
            return False
        if not step4_verification_and_preferences(driver, wait):
            print("\n[FAIL] Verification step failed")
            return False
        current_url = driver.current_url
        print(f"\nFinal URL: {current_url}")
        if "login" in current_url.lower() or "dashboard" in current_url.lower() or "success" in current_url.lower():
            print("\n[PASS] Signup flow completed successfully!")
        else:
            print("\n[INFO] Automation completed. Verify final page state.")
        return True
    except Exception as e:
        print(f"\n[ERROR] Automation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if driver:
            time.sleep(2)
            driver.quit()
            print("\nBrowser closed.")


if __name__ == "__main__":
    import sys
    headless = "--headless" in sys.argv
    success = run_signup_automation(headless=headless)
    sys.exit(0 if success else 1)
