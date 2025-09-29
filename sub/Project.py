from requests import Session

class Project:
    def __init__(self, token):
        self.s = Session()
        self.s.headers = {
            "authorization": f"Token {token}"
        }
    
    def uploadProject(self, name="very good website", desc="coin farmer 3000 | https://github.com/7950x/TekyCoinFarmer"):
        return self.s.post('https://api.teky.edu.vn/du-an-cua-em/api/my-projects/', json={
            "project_type": "session_end",
            "name": name,
            "project_description": desc,
            "project_public": "true",
            "ignoreClass": "0"
        })
    
    def deleteProject(self, id):
            return self.s.delete(f'https://api.teky.edu.vn/du-an-cua-em/api/my-projects/{id}/')