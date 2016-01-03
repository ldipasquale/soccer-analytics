import utils.util
import argparse
from model import *

session = Session()

def get_seasons():
	ids = []
	
	for season_data in util.make_api_request('/soccerseasons'):
		season = Season(
			id = season_data["id"], 
			caption = season_data["caption"], 
			league = season_data["league"], 
			year = season_data["year"],
			current_match_day = season_data["currentMatchday"],
			last_updated = util.build_date(season_data["lastUpdated"])
		)

		session.add(season)

		for team_data in util.make_api_request('/soccerseasons/' + str(season.id) + "/teams")["teams"]:
			team = Team(
				id = util.get_id_from_url(team_data["_links"]["self"]["href"], "teams"),
				name = team_data["name"],
				code = team_data["code"],
				short_name = team_data["shortName"], 
				squad_market_value = team_data["squadMarketValue"], 
				crest_url = team_data["crestUrl"], 
				season_id = season.id, 
			)

			if(not team.id in ids):
				session.add(team)

			ids.append(team.id)

	session.commit()

def get_matches():
	for team in session.query(Team).limit(1).offset(1).all():
		for match_data in util.make_api_request('/teams/' + str(team.id) + '/fixtures')["fixtures"]:
			match = Match(
				id = util.get_id_from_url(match_data["_links"]["self"]["href"], 'fixtures'), 
				date = util.build_date(match_data["date"]),
				status = match_data["status"],
				season_id = util.get_id_from_url(match_data["_links"]["soccerseason"]["href"], 'soccerseasons'), 
				home_team_id = util.get_id_from_url(match_data["_links"]["homeTeam"]["href"], 'teams'), 
				away_team_id = util.get_id_from_url(match_data["_links"]["awayTeam"]["href"], 'teams'), 
				home_score = match_data["result"]["goalsHomeTeam"], 
				away_score = match_data["result"]["goalsAwayTeam"],
				match_day = match_data["matchday"],
			)

			if(session.query(Match).filter(Match.id == match.id).count() == 0):
				session.add(match)	

	session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--seasons', action="count", default=0, required=False)
    parser.add_argument('-m', '--matches', action="count", default=0, required=False)
    args = parser.parse_args()

    if(args.seasons):
    	get_seasons()

    if(args.matches):
    	get_matches()