#!/usr/bin/env python3
"""
ServiceNow Session Manager with Automatic Credential Refresh

Manages authentication sessions and automatically refreshes expired credentials
using headless browser automation with MFA fallback.
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path


INSTANCE_URL = 'https://surf.service-now.com'
CREDENTIALS_FILE = Path.home() / '.servicenow_surf_session.json'


class AuthenticationError(Exception):
    """Raised when authentication fails and cannot be recovered"""
    pass


class ServiceNowSession:
    """
    Manages ServiceNow authentication with automatic refresh on session expiration.

    This session manager transparently handles expired cookies by:
    1. Detecting 401 Unauthorized responses
    2. Attempting headless browser refresh
    3. Falling back to visible browser if MFA is required
    4. Retrying the original request with fresh credentials
    """

    def __init__(self):
        self.cookies = None
        self.x_user_token = None
        self.mfa_refresh_attempted = False  # Track MFA attempts this session
        self.instance_url = INSTANCE_URL
        self.load_credentials()

    def load_credentials(self):
        """Load credentials from cache file or environment variables"""
        # Priority 1: Try environment variables
        x_user_token = os.getenv('SNOW_X_USER_TOKEN')
        glide_cookie = os.getenv('SNOW_COOKIE_GLIDE')
        session_cookie = os.getenv('SNOW_COOKIE_SESSION')

        if x_user_token and glide_cookie and session_cookie:
            self.x_user_token = x_user_token
            self.cookies = {
                'glide_user_route': glide_cookie,
                'JSESSIONID': session_cookie
            }
            return

        # Priority 2: Try cached credentials file
        if CREDENTIALS_FILE.exists():
            try:
                with open(CREDENTIALS_FILE, 'r') as f:
                    creds = json.load(f)

                self.x_user_token = creds.get('x_user_token')
                self.cookies = creds.get('cookies', {})

                # Check age
                timestamp = creds.get('timestamp')
                if timestamp:
                    saved_time = datetime.fromisoformat(timestamp)
                    age_hours = (datetime.now() - saved_time).total_seconds() / 3600
                    age_minutes = age_hours * 60

                    # Warn if credentials are getting old
                    if age_minutes > 25:
                        pass  # Will be checked automatically on first request
                return
            except Exception as e:
                print(f"⚠️  Failed to load cached credentials: {e}")

        # No credentials found
        self.x_user_token = None
        self.cookies = {}

    def save_credentials(self):
        """Save credentials to cache file"""
        credentials = {
            'cookies': self.cookies,
            'x_user_token': self.x_user_token,
            'glide_user_route': self.cookies.get('glide_user_route'),
            'jsessionid': self.cookies.get('JSESSIONID'),
            'timestamp': datetime.now().isoformat()
        }

        try:
            with open(CREDENTIALS_FILE, 'w') as f:
                json.dump(credentials, f, indent=2)
            return True
        except Exception as e:
            print(f"⚠️  Failed to save credentials: {e}")
            return False

    def refresh_credentials(self, headless=False, interactive_fallback=True):
        """
        Trigger browser automation to get fresh cookies.

        Args:
            headless: Try headless mode first (invisible browser) - disabled by default since MFA is required
            interactive_fallback: If headless fails due to MFA, retry with visible browser

        Returns:
            True if successful, False if cannot refresh
        """
        try:
            from .login_and_extract import get_session_from_browser
        except ImportError:
            print("❌ Cannot import login_and_extract module")
            return False

        print("🔄 Attempting automatic credential refresh...")

        # Skip headless mode by default since Okta MFA is required
        # Try headless first only if explicitly requested
        if headless:
            cookies, token = get_session_from_browser(use_chrome=True, headless=True)

            if cookies and token:
                self.cookies = cookies
                self.x_user_token = token
                self.save_credentials()
                return True

        # Go straight to interactive mode (visible browser) for MFA
        if interactive_fallback and not self.mfa_refresh_attempted:
            # Open visible browser for Okta MFA authentication
            print("\n🔒 Opening browser for authentication...")
            print("Please complete login and MFA when prompted.")
            self.mfa_refresh_attempted = True

            cookies, token = get_session_from_browser(use_chrome=True, headless=False)

            if cookies and token:
                self.cookies = cookies
                self.x_user_token = token
                self.save_credentials()
                return True

        return False

    def test_credentials(self):
        """
        Quick API call to validate if current session is valid.

        Returns:
            True if credentials are valid, False otherwise
        """
        if not self.cookies or not self.x_user_token:
            return False

        try:
            url = f'{self.instance_url}/api/now/table/sys_user'
            headers = {'X-UserToken': self.x_user_token}
            response = requests.get(
                url,
                headers=headers,
                cookies=self.cookies,
                params={'sysparm_limit': 1},
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def _get_headers(self):
        """Build headers dict for requests"""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        if self.x_user_token:
            headers['X-UserToken'] = self.x_user_token
        return headers

    def request(self, method, url, **kwargs):
        """
        Wrapper around requests with automatic retry on 401.

        This method transparently handles session expiration by:
        1. Making the original request
        2. If 401 Unauthorized → refresh credentials and retry
        3. If still 401 after refresh → raise AuthenticationError

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: Full URL to request
            **kwargs: Additional arguments to pass to requests

        Returns:
            requests.Response object

        Raises:
            AuthenticationError: If credential refresh fails or credentials are invalid
        """
        # Ensure we have credentials
        if not self.cookies or not self.x_user_token:
            print("⚠️  No credentials found - triggering authentication...")
            if not self.refresh_credentials(headless=False, interactive_fallback=True):
                raise AuthenticationError("No credentials available and refresh failed")

        # Add headers and cookies to kwargs
        if 'headers' not in kwargs:
            kwargs['headers'] = {}
        kwargs['headers'].update(self._get_headers())

        if 'cookies' not in kwargs:
            kwargs['cookies'] = self.cookies

        # Make the request
        response = requests.request(method, url, **kwargs)

        # Handle 401 Unauthorized (expired session)
        if response.status_code == 401:
            print("⚠️  Session expired (401 Unauthorized)")

            if self.refresh_credentials(headless=False, interactive_fallback=True):
                print("✅ Credentials refreshed successfully")
                print("🔄 Retrying original request...")

                # Update headers and cookies with fresh credentials
                kwargs['headers'].update(self._get_headers())
                kwargs['cookies'] = self.cookies

                # Retry the original request
                response = requests.request(method, url, **kwargs)

                if response.status_code == 401:
                    print("❌ Still getting 401 after refresh - credentials may be invalid")
                    raise AuthenticationError("Credential refresh failed to resolve 401 error")
            else:
                print("\n❌ Automatic refresh failed")
                print("\nManual authentication required:")
                print("  1. Run: python src/servicenow_skill/utils/login_and_extract.py")
                print("  2. Complete the login and MFA prompts")
                print("  3. Re-run your original command")
                raise AuthenticationError("Unable to refresh credentials automatically")

        return response

    def get(self, url, **kwargs):
        """Convenience method for GET requests"""
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        """Convenience method for POST requests"""
        return self.request('POST', url, **kwargs)

    def put(self, url, **kwargs):
        """Convenience method for PUT requests"""
        return self.request('PUT', url, **kwargs)

    def delete(self, url, **kwargs):
        """Convenience method for DELETE requests"""
        return self.request('DELETE', url, **kwargs)

    def patch(self, url, **kwargs):
        """Convenience method for PATCH requests"""
        return self.request('PATCH', url, **kwargs)


def main():
    """Test the session manager"""
    print("Testing ServiceNow Session Manager\n")

    session = ServiceNowSession()

    print("Current credentials:")
    print(f"  X-UserToken: {'✅ Found' if session.x_user_token else '❌ Not found'}")
    print(f"  Cookies: {len(session.cookies)} found\n")

    if session.x_user_token:
        print("Testing credentials...")
        if session.test_credentials():
            print("✅ Credentials are valid!\n")
        else:
            print("❌ Credentials are invalid or expired\n")

    print("Making a test API request...")
    try:
        url = f'{INSTANCE_URL}/api/now/table/sys_user'
        response = session.get(url, params={'sysparm_limit': 1})

        if response.status_code == 200:
            data = response.json()
            count = len(data.get('result', []))
            print(f"✅ Request successful! Retrieved {count} records")
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
    except AuthenticationError as e:
        print(f"❌ Authentication error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == '__main__':
    main()
