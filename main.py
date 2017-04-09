
from github import Github

with open("../p.txt", "r") as f:
    lines = f.readlines()
    user = lines[0].strip()
    pw = lines[1].strip()

g = Github("nwalsh1995", pw)

for repo in g.get_user().get_repos():
    print repo.name