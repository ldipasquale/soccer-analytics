import json, requests, datetime, re

api = 'http://api.football-data.org/v1'

def make_api_request(url):
	headers = {'X-Auth-Token': '9439cac711394ee0851fe1113408e38a'}
	resp = requests.get(url = api + url, headers=headers)
	data = json.loads(resp.text)

	return data

def build_date(str):
	return datetime.datetime.strptime(str, "%Y-%m-%dT%H:%M:%SZ")

def get_id_from_url(str, method):
	m = re.search(api + "/" + method + "/(\d+)", str)
	if m:
		return int(m.groups()[0])

	return ''