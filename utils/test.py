import re
m = re.search("http://api.football-data.org/v1/teams/(\d+)", "http://api.football-data.org/v1/teams/7")
if m:
    print(m.groups()[0])