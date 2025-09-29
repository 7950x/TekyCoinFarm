from sub import Project, Login
from os import environ

loginHelper = Login()
token = loginHelper.Login(environ['USERNAME'], environ['PASSWORD'])

print('logged in')

projectHelper = Project(token)
projectHelper.deleteProject(projectHelper.uploadProject().json()['data']['id'])

print('cycle completed')