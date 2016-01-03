from houses.miljugadas import *
import argparse
from pprint import pprint
from operator import attrgetter

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument('--betting_house', default='miljugadas')
	parser.add_argument('--leagues', default='all')
	parser.add_argument('--days', default=2, type=int)
	parser.add_argument('--matches', default=5, type=int)
	parser.add_argument('--hardcoding', default=False)
	args = parser.parse_args()

	session = Session()

	if(args.betting_house == "miljugadas"):
		matches = miljugadas(args.leagues, args.days, args.hardcoding)

	bettable_matches = []
	for match in matches:
		if match.is_bettable(session, args.matches):
			bettable_matches.append(match)

	bettable_matches.sort(key=attrgetter('points'), reverse=True)

	pprint(bettable_matches)
