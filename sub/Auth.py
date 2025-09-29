from requests import Session
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import traceback

class Login:
    def __init__(self, debug=True):
        self.s = Session()
        self.debug = debug

    def log(self, message):
        """Helper function for debug logging"""
        if self.debug:
            print(f"[DEBUG] {message}")

    @staticmethod
    def parseCSRF(CSRFReq):
        try:
            soup = BeautifulSoup(CSRFReq.text, "html.parser")
            tag = soup.find("input", attrs={"name": "authenticity_token"})
            CSRFToken = tag["value"] if tag else None
            if not CSRFToken:
                print("❌ CSRF Token not found. Please create an issue with logs.")
            return CSRFToken
        except Exception:
            print("⚠️ Error while parsing CSRF token:")
            traceback.print_exc()
            return None

    def getFirstCSRF(self):
        url = (
            "https://accounts.teky.edu.vn/v1/oauth/authorize"
            "?response_type=code"
            "&client_id=feMSCND4VsM_S1jJTfSUWSxtzTgcB7FIV8o9NZzh0nY"
            "&redirect_uri=https://teky.edu.vn/auth/sso-callback"
            "&state=state"
        )
        self.log(f"Fetching initial CSRF token from: {url}")
        try:
            CSRFReq = self.s.get(url)
            self.log(f"Status code: {CSRFReq.status_code}")
            token = self.parseCSRF(CSRFReq)
            self.log(f"Extracted CSRF Token: {token}")
            return token
        except Exception:
            print("❌ Failed to get initial CSRF token.")
            traceback.print_exc()
            return None

    def Login(self, username, password):
        try:
            csrf_token = self.getFirstCSRF()
            if not csrf_token:
                raise ValueError("No CSRF token found before login!")

            login_url = "https://accounts.teky.edu.vn/users/sign_in?locale=vi"
            self.log(f"Sending login request to: {login_url}")
            LoginReq = self.s.post(
                login_url,
                data={
                    "authenticity_token": csrf_token,
                    "user[username]": username,
                    "user[password]": password,
                    "commit": "Đăng nhập",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            self.log(f"Login response status: {LoginReq.status_code}")
            if LoginReq.status_code != 200:
                print("❌ Login request failed.")
                return None

            soup = BeautifulSoup(LoginReq.text, "html.parser")
            id_tag = soup.find("input", {"name": "student_id"})
            if not id_tag:
                print("❌ Student ID input not found in login response.")
                return None

            student_id = id_tag.get("value")
            self.log(f"Found student_id: {student_id}")

            student_login_url = "https://accounts.teky.edu.vn/users/login_with_student?locale=vi"
            self.log(f"Logging in with student_id at: {student_login_url}")

            csrf_after_login = self.parseCSRF(LoginReq)
            if not csrf_after_login:
                print("⚠️ Missing CSRF token for student login request.")

            StudentReq = self.s.post(
                student_login_url,
                data={
                    "authenticity_token": csrf_after_login,
                    "student_id": student_id,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            self.log(f"Student login status: {StudentReq.status_code}")
            self.log(f"Redirect URL: {StudentReq.url}")

            parsed_url = urlparse(StudentReq.url)
            query_params = parse_qs(parsed_url.query)
            self.log(f"Query parameters: {query_params}")

            if 'code' not in query_params:
                print("❌ No 'code' parameter found in redirect URL.")
                return None

            code = query_params['code'][0]
            self.log(f"Authorization code: {code}")

            final_url = "https://api.teky.edu.vn/api/v2/auth/token/"
            self.log(f"Exchanging code for token at: {final_url}")

            final = self.s.post(
                final_url,
                json={
                    "code": code,
                    "redirect_uri": "https://teky.edu.vn/auth/sso-callback",
                    "state": "state",
                },
            )

            self.log(f"Final response status: {final.status_code}")
            self.log(f"Response text: {final.text}")

            token_json = final.json()
            token = token_json.get('data', {}).get('token')

            if not token:
                print("❌ Token not found in final response.")
                return None

            self.log(f"✅ Successfully retrieved token: {token}")
            return token

        except Exception:
            print("❌ An unexpected error occurred during login.")
            traceback.print_exc()
            return None
