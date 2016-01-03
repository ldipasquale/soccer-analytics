from model import *
from datetime import date, timedelta
from bs4 import BeautifulSoup
from houses.const import *

import requests, re

def miljugadas(leagues_param = 'all', days = 2, hardcoding = false):
	if hardcoding:
		return [
			Match('West Ham', 'Liverpool', 398, {'draw': 3.3, 'away': 2.05, 'home': 3.75}), 
			Match('Arsenal', 'Newcastle United', 398, {'draw': 5.75, 'away': 11.0, 'home': 1.26}), 
			Match('Leicester', 'Bournemouth', 398, {'draw': 3.6, 'away': 3.75, 'home': 1.95}), 
			Match('Manchester United', 'Swansea', 398, {'draw': 3.75, 'away': 6.75, 'home': 1.55}), 
			Match('Norwich', 'Southampton', 398, {'draw': 3.3, 'away': 2.35, 'home': 3.0}), 
			Match('Sunderland', 'Aston Villa', 398, {'draw': 3.1, 'away': 3.05, 'home': 2.45}), 
			Match('West Brom', 'Stoke City', 398, {'draw': 3.0, 'away': 2.65, 'home': 2.875}), 
			Match('Watford', 'Manchester City', 398, {'draw': 3.75, 'away': 1.72, 'home': 4.6}), 
			Match('Espanyol', 'Barcelona', 399, {'draw': 6.25, 'away': 1.22, 'home': 12.0}), 
			Match('Atlético de Madrid', 'Levante', 399, {'draw': 6.0, 'away': 17.0, 'home': 1.2}), 
			Match('Málaga', 'Celta', 399, {'draw': 3.15, 'away': 3.15, 'home': 2.35})
		]
	else:
		session = Session()

		if leagues_param == 'all':
			leagues = {}
			leagues_codes = {}
			for season in session.query(SeasonHouse).join(House, House.slug == "miljugadas").join(Season):
				leagues_codes[season.caption] = season.season_house_id
				leagues[season.caption] = season.season_id

		leagues_str = re.search('\((.*?)\)', str(leagues_codes.values())).group(1)
		url = 'https://www.miljugadas.com/es-ES/sportsbook/eventpaths/multi/' + leagues_str

		req = requests.get(url)

		soup = BeautifulSoup(req.text)

		available_matches = []

		for day_matches in soup.find('div', {'class': 'rollup market_type market_type_id_1 win_draw_win multi_event game_type'}).find_all('div', {'class': 'rollup event_date'}):
			matches_day, matches_month = day_matches.find('h2', {'class': 'event_date-title'}).contents[0].split(' ')[1:]

			today = date.today()
			match_date = date(match_date_year + 1 if MONTHS[matches_month] == 1 and today.month == 12 else today.year, MONTHS[matches_month], int(matches_day))

			if match_date - today <= timedelta(days):
				for league_matches in day_matches.find_all('div', {'class': 'event_path'}):
					league = league_matches.find('h2', {'class': 'event_path_title ellipsis'}).contents[0]

					if league in leagues.keys():
						for match in league_matches.find_all('tr', {'class': 'event'}):
							home, draw, away = match.find_all('a')
							home_team = home.span['title']
							home_win = float(home['data-price-decimal'])
							draw = float(draw['data-price-decimal'])
							away_team = away.span['title']
							away_win = float(away['data-price-decimal'])
							prizes = {'home': home_win, 'draw': draw, 'away': away_win}

							if not 'Home Teams Goals' in home_team:
								match = Match(home_team, away_team, leagues[league], prizes, match_date)

								available_matches.append(match)

		return available_matches
