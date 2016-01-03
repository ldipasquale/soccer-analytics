from sqlalchemy import *
from model import Base, Engine

if __name__ == '__main__':
	Base.metadata.create_all(Engine, checkfirst=True)