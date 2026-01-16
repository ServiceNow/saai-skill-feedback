#!/usr/bin/env python3
"""
Login to ServiceNow via browser and extract session credentials.

Adapted from your fetch_servicenow_automated.py
"""

import os
import sys
import time
import json

# Check for selenium
try:
    from selenium import webdriver
    from selenium.webdriver.safari.options import Options as SafariOptions
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.support.ui import WebDriverWait
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        HAS_WEBDRIVER_MANAGER = True
    except ImportError:
        HAS_WEBDRIVER_MANAGER = False
except ImportError:
    print("❌ selenium is not installed.")
    print("\nInstall with:")
    print("  pip3 install selenium")
    print("\nOptionally for Chrome auto-driver:")
    print("  pip3 install webdriver-manager")
    sys.exit(1)

INSTANCE_URL = 'https://surf.service-now.com'
CREDENTIALS_FILE = os.path.expanduser('~/.servicenow_surf_session.json')

def save_credentials(cookies, x_user_token):
    """Save credentials to disk for the skill to use"""
    from datetime import datetime

    credentials = {
        'cookies': cookies,
        'x_user_token': x_user_token,
        'glide_user_route': cookies.get('glide_user_route'),
        'jsessionid': cookies.get('JSESSIONID'),
        'timestamp': datetime.now().isoformat()
    }

    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials, f, indent=2)
        print(f"\n✅ Credentials saved to {CREDENTIALS_FILE}")
        return True
    except Exception as e:
        print(f"⚠️  Failed to save credentials: {e}")
        return False

def get_session_from_browser(use_chrome=True, headless=False):
    """
    Use Selenium to automate login and extract session credentials

    Args:
        use_chrome: Use Chrome browser (else Safari)
        headless: Run browser in headless mode (invisible)

    Returns:
        (cookies_dict, x_user_token) tuple or (None, None) if MFA blocks automation
    """
    print("ServiceNow Automated Login")
    print("="*80)

    # Choose browser
    driver = None
    if use_chrome and HAS_WEBDRIVER_MANAGER:
        if headless:
            print("Opening Chrome in headless mode (invisible)...")
        else:
            print("Opening Chrome browser...")
        print("(Installing/updating Chrome driver if needed...)\n")
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        # Add headless mode arguments
        if headless:
            options.add_argument('--headless=new')  # New headless mode
            options.add_argument('--disable-gpu')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')

        try:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"❌ Failed to open Chrome: {e}")
            if headless:
                print("\n❌ Headless Chrome failed - cannot fall back to Safari in headless mode")
                return None, None
            print("\nFalling back to Safari...")
            use_chrome = False

    if not driver:
        print("Opening Safari browser...")
        print("\n⚠️  NOTE: Safari automation must be enabled first:")
        print("   Run: sudo safaridriver --enable")
        print("   OR go to Safari > Develop > Allow Remote Automation\n")
        try:
            options = SafariOptions()
            driver = webdriver.Safari(options=options)
        except Exception as e:
            print(f"❌ Failed to open Safari: {e}")
            print("\nMake sure Safari allows remote automation.")
            print("Run: sudo safaridriver --enable")
            return None, None

    if not headless:
        print("Please log in through Okta when prompted.")
        print("The browser will close automatically after successful login.\n")

    try:
        # Navigate to ServiceNow
        driver.get(INSTANCE_URL)

        if headless:
            print("Attempting headless authentication...")
            print("(Will detect if MFA is required)\n")
        else:
            print("Waiting for you to complete Okta authentication...")
            print("(Timeout: 5 minutes)\n")

        # Wait for authentication to complete
        wait = WebDriverWait(driver, 300 if not headless else 30)  # 30 sec for headless

        # Check if we hit an MFA page
        time.sleep(2)  # Give page time to load

        current_url = driver.current_url.lower()
        page_source = driver.page_source.lower() if driver.page_source else ""

        # Detect MFA challenge pages
        mfa_indicators = [
            'okta-verify' in current_url,
            'mfa' in current_url,
            'multifactor' in current_url,
            'duo' in current_url,
            'verify your identity' in page_source,
            'authentication required' in page_source,
            'push notification' in page_source,
        ]

        if any(mfa_indicators) and headless:
            print("🔒 MFA detected - cannot complete authentication in headless mode")
            return None, None

        # Wait until we're back on the ServiceNow domain
        wait.until(lambda d: INSTANCE_URL in d.current_url)

        print("✅ Authentication detected! Extracting credentials...")
        time.sleep(3)  # Give it a moment to fully load

        # Get all cookies
        cookies = driver.get_cookies()

        # Convert to dictionary format
        cookies_dict = {}
        for cookie in cookies:
            cookies_dict[cookie['name']] = cookie['value']

        # Try to get X-UserToken from window.g_ck
        x_user_token = None

        try:
            x_user_token = driver.execute_script("return window.g_ck;")
            if x_user_token:
                print(f"✅ Found X-UserToken: {x_user_token[:20]}...")
        except:
            pass

        # If we didn't get the token, try making an API call
        if not x_user_token:
            print("Attempting to capture X-UserToken from API request...")
            try:
                test_url = f"{INSTANCE_URL}/api/now/table/sys_user?sysparm_limit=1"
                driver.get(test_url)
                time.sleep(2)

                x_user_token = driver.execute_script("return window.g_ck;")
                if x_user_token:
                    print(f"✅ Captured X-UserToken: {x_user_token[:20]}...")
            except:
                pass

        print("\n" + "="*80)
        print("Session Credentials Extracted")
        print("="*80)
        print(f"Cookies: {len(cookies_dict)} found")
        print(f"X-UserToken: {'✅ Found' if x_user_token else '❌ Not found'}")
        print("="*80 + "\n")

        return cookies_dict, x_user_token

    except Exception as e:
        print(f"\n❌ Error during authentication: {e}")
        return None, None
    finally:
        print("Closing browser...")
        driver.quit()

def print_env_vars(cookies_dict, x_user_token):
    """Print environment variables to set"""
    print("\n" + "="*80)
    print("SET THESE ENVIRONMENT VARIABLES")
    print("="*80)
    print()
    print(f'export SNOW_X_USER_TOKEN="{x_user_token}"')
    print(f'export SNOW_COOKIE_GLIDE="{cookies_dict.get("glide_user_route", "")}"')
    print(f'export SNOW_COOKIE_SESSION="{cookies_dict.get("JSESSIONID", "")}"')
    print()
    print("Make them permanent:")
    print()
    print(f'echo \'export SNOW_X_USER_TOKEN="{x_user_token}"\' >> ~/.zshrc')
    print(f'echo \'export SNOW_COOKIE_GLIDE="{cookies_dict.get("glide_user_route", "")}"\' >> ~/.zshrc')
    print(f'echo \'export SNOW_COOKIE_SESSION="{cookies_dict.get("JSESSIONID", "")}"\' >> ~/.zshrc')
    print('source ~/.zshrc')
    print()
    print("="*80)

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Extract ServiceNow session credentials')
    parser.add_argument('--headless', action='store_true',
                       help='Run browser in headless mode (invisible)')
    parser.add_argument('--browser', choices=['chrome', 'safari'], default='chrome',
                       help='Browser to use (default: chrome)')
    args = parser.parse_args()

    print("\n")
    print("="*80)
    print("SERVICENOW CREDENTIAL EXTRACTOR")
    print("="*80)
    print()

    # Determine browser choice
    if not sys.stdin.isatty() or args.headless or args.browser != 'chrome':
        # Non-interactive mode or explicit browser choice
        use_chrome = (args.browser == 'chrome')
    else:
        # Ask user which browser
        print("Browser Options:")
        if HAS_WEBDRIVER_MANAGER:
            print("1. Chrome (recommended - auto-installs driver)")
        else:
            print("1. Chrome (requires chromedriver installed)")
        print("2. Safari (requires: sudo safaridriver --enable)")
        choice = input("\nSelect browser (1-2, default=1): ").strip() or "1"
        use_chrome = (choice == "1")

    # Get session credentials
    cookies_dict, x_user_token = get_session_from_browser(
        use_chrome=use_chrome,
        headless=args.headless
    )

    if not cookies_dict:
        print("\n❌ Failed to get session credentials")
        return 1

    if not x_user_token:
        print("\n⚠️  Warning: Could not extract X-UserToken")
        print("The credentials may not work for API access.")
        print()
        return 1

    # Save credentials
    if save_credentials(cookies_dict, x_user_token):
        print()
        print("✅ Credentials saved successfully!")
        print()
        print("These credentials will be automatically loaded by the skill.")
        print()

    # Print env vars
    print_env_vars(cookies_dict, x_user_token)

    # Test the credentials
    print("\nTest your credentials:")
    print("  python scripts/test_auth.py")
    print()

    return 0

if __name__ == '__main__':
    sys.exit(main())
