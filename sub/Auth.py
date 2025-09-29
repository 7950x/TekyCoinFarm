from requests import Session
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

class Login:
    def __init__(self):
        self.s = Session()

    @staticmethod
    def parseCSRF(CSRFReq):
        soup = BeautifulSoup(CSRFReq.text, "html.parser")
        tag = soup.find("input", attrs={"name": "authenticity_token"})
        CSRFToken = (
            tag["value"]
            if tag
            else print("CSRF Token not found. Please create an issue with logs.")
        )
        return CSRFToken

    def getFirstCSRF(self):
        CSRFReq = self.s.get(
            "https://accounts.teky.edu.vn/v1/oauth/authorize?response_type=code&client_id=feMSCND4VsM_S1jJTfSUWSxtzTgcB7FIV8o9NZzh0nY&redirect_uri=https://teky.edu.vn/auth/sso-callback&state=state"
        )
        return self.parseCSRF(CSRFReq)

    def Login(self, username, password):
        LoginReq = self.s.post(
            "https://accounts.teky.edu.vn/users/sign_in?locale=vi",
            data={
                "authenticity_token": self.getFirstCSRF(),
                "user[username]": username,
                "user[password]": password,
                "commit": "Đăng nhập",
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        print(LoginReq.text)

        soup = BeautifulSoup(LoginReq.text, "html.parser")
        id = soup.find("input", {"name": "student_id"}).get("value")

        StudentReq = self.s.post(
            "https://accounts.teky.edu.vn/users/login_with_student?locale=vi",
            data={
                "authenticity_token": self.parseCSRF(LoginReq),
                "student_id": id,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        final = self.s.post(
            "https://api.teky.edu.vn/api/v2/auth/token/",
            json={
                "code": parse_qs(urlparse(StudentReq.url).query)['code'][0],
                "redirect_uri": "https://teky.edu.vn/auth/sso-callback",
                "state": "state",
            },
        )
        return final.json()['data']['token']