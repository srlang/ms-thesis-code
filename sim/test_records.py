
from sqlalchemy.orm import sessionmaker
#from sqlalchemy import *


def basic_setup():
    engine = None
    Session = sessionmaker(bind=engine)
    return Session()

def test_PlayedHandRecord():
    pass

