from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pprint import pprint

Base = declarative_base()
Engine = create_engine('sqlite:///soccer.db')
Session = sessionmaker(bind=Engine)

class House(Base):
	__tablename__ = 'houses'

	id = Column(Integer, primary_key=True)
	name = Column(String(50), nullable=True)
	slug = Column(String(50), nullable=True)

class Season(Base):
	__tablename__ = 'seasons'

	id = Column(Integer, primary_key=True)
	caption = Column(String(50), nullable=True)
	league = Column(String(50))
	year = Column(Integer, nullable=True)
	current_match_day = Column(Integer, nullable=True)
	last_updated = Column(DateTime, nullable=True)

class SeasonHouse(Base):
	__tablename__ = 'seasons_houses'

	id = Column(Integer, primary_key=True)
	season_id = Column(ForeignKey('seasons.id'))
	season_house_id = Column(Integer)
	caption = Column(String(80), nullable=True)
	house_id = Column(ForeignKey('houses.id'))

class Team(Base):
	__tablename__ = 'teams'

	id = Column(Integer, primary_key=True)
	name = Column(String(50))
	code = Column(String(50), nullable=True)
	short_name = Column(String(50), nullable=True)
	squad_market_value = Column(String(50), nullable=True)
	crest_url = Column(String(200), nullable=True)
	season_id = Column(ForeignKey('seasons.id'))

	def __init__(self, name, condition, season_id):
		self.name = name
		self.season_id = season_id
		self.condition = condition
		self.points = 0
		self.last_matches = {"win": 0, "draw": 0, "lost": 0}

	def is_home(self):
		return self.condition == "home"

	def lost_match(self):
		self.last_matches["lost"] += 1

	def win_match(self):
		self.last_matches["win"] += 1
		self.points += 3

	def draw_match(self):
		self.last_matches["draw"] += 1
		self.points += 1

	def get_lost_matches(self):
		return self.last_matches["lost"]

	def get_win_matches(self):
		return self.last_matches["win"]

	def get_draw_matches(self):
		return self.last_matches["draw"]


	def get_performance(self, session, amount):
		team = session.query(Team).filter(and_(Team.season_id == self.season_id, or_(Team.name == self.name + " FC", Team.name == self.name, Team.short_name == self.name))).first()

		if team:
			condition_column = "home_team_id" if self.is_home() else "away_team_id"
			matches = session.query(Match).filter(and_(getattr(Match, condition_column) == team.id, Match.season_id == self.season_id, Match.status == "FINISHED")).order_by(Match.date.desc()).limit(amount).all()

			for match in matches:
				if match.home_score == match.away_score:
					self.draw_match()
				elif (self.is_home() and match.home_score > match.away_score) or (not self.is_home() and match.home_score < match.away_score):
					self.win_match()
				else:
					self.lost_match()

			if(self.points == 0):
				self.points = 1

			self.performance = self.points / amount

			return True
		else:
			print(self.name + " (" + str(self.season_id) + ") was not found in the database")

			return False


class Match(Base):
	__tablename__ = 'matches'

	id = Column(Integer, primary_key=True)
	date = Column(DateTime)
	home_team_id = Column(String(50), nullable=True)
	away_team_id = Column(String(50), nullable=True)
	home_score = Column(Integer, nullable=True)
	away_score = Column(Integer, nullable=True)
	match_day = Column(Integer)
	season_id = Column(Integer)
	status = Column(String(100))

	def __init__(self, home_team, away_team, season_id, prizes, date = None):
		self.home_team = Team(home_team, 'home', season_id)
		self.away_team = Team(away_team, 'away', season_id)
		self.date = date
		self.prizes = prizes
		self.favorite_team = None

	def is_bettable(self, session, matches_amount = 5):
		if self.home_team.get_performance(session, matches_amount) and self.away_team.get_performance(session, matches_amount):
			if self.home_team.performance > self.away_team.performance:
				self.favorite_team = self.home_team
				self.favorite_prizes = self.prizes["home"]
				self.versus_team = self.away_team
				self.versus_prizes = self.prizes["away"]
				self.points = self.home_team.performance / self.away_team.performance * self.prizes["home"]
			elif self.home_team.performance < self.away_team.performance:
				self.favorite_team = self.away_team
				self.favorite_prizes = self.prizes["away"]
				self.versus_team = self.home_team
				self.versus_prizes = self.prizes["home"]
				self.points = self.away_team.performance / self.home_team.performance * self.prizes["away"]

			if self.favorite_team:
				self.points = round(self.points, 2)

				if self.favorite_team.get_win_matches() >= 4 and self.versus_team.get_lost_matches() >= 4:
					return True
		return False



	def __repr__(self):
		if(self.points):
			return self.favorite_team.name + " (" + str(self.favorite_prizes) + ") will beat " + self.versus_team.name + " (" + str(self.versus_prizes) + ") - " + str(self.points) + " points - " + str(self.date)
		else:
			return ""