# Sean R. Lang <sean.lang@cs.helsinki.fi>

from sqlalchemy                 import Column, Integer, Float, String
from sqlalchemy                 import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker

from config import SQL_ENGINE, SQL_ECHO

engine = create_engine(SQL_ENGINE, echo=SQL_ECHO)
Base = declarative_base()
Session = sessionmaker(bind=engine)


def create_tables():
    global Base
    global engine
    Base.metadata.create_all(engine)


class PlayedHandRecord(Base):

    '''
    Keep track of how a hand was played in a single round.
    '''

    # keeping track of played hands
    __tablename__ = 'played_hands'

    # primary key for sanity
    id = Column(Integer, primary_key=True)

    # keep track of each card individually for quicker comparison
    # N.B. For the sake of easier search, keep these in value order
    #      This is true for the rest of the simulation anyways, but just
    #      another reinforcement.
    card0 = Column(Integer)
    card1 = Column(Integer)
    card2 = Column(Integer)
    card3 = Column(Integer)

    # how many points were gained from play
    score_gained = Column(Integer)
    # how many points were yielded to the opponent in play
    score_given = Column(Integer)

    pass

class AggregatePlayedHandRecord(Base):

    '''
    Keep an aggregate record of all accounts of a single 4-card hand that has
    been played.
    Keep this updated regularly.
    This is created to allow the implementation to avoid unnecessary, resource-
    consuming database queries all the time.
    '''

    __tablename__ = 'aggregate_played_hands'

    id = Column(Integer, primary_key=True)

    # indexing cards
    card0 = Column(Integer)
    card1 = Column(Integer)
    card2 = Column(Integer)
    card3 = Column(Integer)

    # Statistics for the values of score_gained
    gained_min = Column(Integer)
    gained_max = Column(Integer)
    gained_avg = Column(Float)
    gained_med = Column(Float)
    gained_mod = Column(Integer)

    # statistics over the values of score_given
    given_min = Column(Integer)
    given_max = Column(Integer)
    given_avg = Column(Float)
    given_med = Column(Float)
    given_mod = Column(Integer)

    # number of times this record has been access modulo <modest power of 2>
    # This way, the implementation can update the record every time the integer
    #   of the log_2 of the access_counter changes.
    #   If the reset modulo parameter is 128, then on average, this saves 3-4
    #   record refreshes every 100 records.
    #   However, this comes at a cost of potentially "losing" 64 records.
    #   It's a payoff I'll have to think about a bit more later down the line
    # The main idea is that this will be visited only when it is chosen
    #   which is FALSE, so this needs to be better
    #access_counter = Column(Integer)
    # Instead let's have the records inserter also update this with a number
    # of the records available (sort of)
    # Keep the same updating as the access_counter, but refresh on this instead
    # N.B. Not an accurate count for the actual number of records
    records_refresh_counter = Column(Integer)
    pass

access_AggregatePlayedHandRecord_counter = 0
def access_AggregatePlayedHandRecord(cards):
    global access_AggregatePlayedHandRecord_counter
    global session
    # TODO
    access_AggregatePlayedHandRecord_counter += 1
    pass

input_PlayedHandRecord_counter = 0
def input_PlayedHandRecord(cards, gained, given):
    global input_PlayedHandRecord_counter
    global session
    # TODO
    input_PlayedHandRecord_counter += 1
    pass

class RawHandStatistics(Base):

    __tablename__ = 'raw_hands_stats'

    card0 = Column(Integer)
    card1 = Column(Integer)
    card2 = Column(Integer)
    card3 = Column(Integer)

    # TODO
    min = Column(Integer)
    max = Column(Integer)
    med = Column(Integer)
    avg = Column(Integer)
    pass


#class ThrowStatistics(Base):
#
#    __tablename__ = 'throw_stats'
#
#    card0 = Column(Integer)
#    card1 = Column(Integer)
#    card2 = Column(Integer)
#    card3 = Column(Integer)
#
#    min = Column(Integer)
#    max = Column(Integer)
#    med = Column(Integer)
#    avg = Column(Integer)


class KeepThrowStatistics(Base):

    # This table's statistics deal only with the counting phase of the game.
    # Pegging will only be taken into account in its own database table.
    #   This is because pegging is varies so much already that the additional
    #   variance from the thrown cards are not really all that important.

    __tablename__ = 'keep_throw_stats'

    # Cards kept in the player's own hand
    kcard0 = Column(Integer)
    kcard1 = Column(Integer)
    kcard2 = Column(Integer)
    kcard3 = Column(Integer)

    # Cards thrown into the crib
    tcard0 = Column(Integer)
    tcard1 = Column(Integer)

    # Statistics for the
    kmin = Column(Integer)
    kmax = Column(Integer)
    kmed = Column(Float)
    kavg = Column(Float)
    kmod = Column(Integer)

    tmin = Column(Integer)
    tmax = Column(Integer)
    tmed = Column(Float)
    tavg = Column(Float)
    tmod = Column(Integer)


def populate_keep_throw_statistics(start_keep=[0, 1, 2, 3], start_throw=[4,5]):
    # TODO: connection stuff

    # Connect to database

    # Find keep/throw possibilities
    # Run through possibilities
    failed = 0
    increased = 0
    for keep,throw in possible_keep_throws:
        try:
            inc = _populate_keep_throw_statistics(keep, throw)
            increased += 1 if inc else 0
            if increased % POPULATE_SAVE_INTERVAL == 0:
                # commit transactions every so often to avoid unnecessary
                # slowing down but also avoid losing all progress due to some
                # stupid error occurring midway
                session.commit()
        except:
            # Database interaction failed
            failed += 1

    # make sure to commit all pending transactions at the end of insertions
    session.commit()


def _populate_keep_throw_statistics(keep, throw):
    # Populate the individual keep/throw possibility with all statistics
    # as desired.
    # Dumb method. No handling of any exceptions, etc.
    found_data = KeepThrowStatistics.query(kcard0=keep[0]).\
                    filter_by(kcard1=keep[1]).\
                    filter_by(kcard2=keep[2]).\
                    filter_by(kcard3=keep[3]).\
                    filter_by(tcard0=throw[0]).\
                    filter_by(tcard1=throw[1])
    if found_data is None:
        # Calculate statistics and add to database
        # TODO
        # Calculate statistics
        keep_vals = []
        throw_vals = []

        # add new row to database
        to_add = KeepThrowStatistics(
                    # kept cards
                    kcard0=keep[0],
                    kcard1=keep[1],
                    kcard2=keep[2],
                    kcard3=keep[3],
                    # thrown cards
                    tcard0=throw[0],
                    tcard1=throw[1],
                    # Keep stats
                    kmin=min(keep_vals),
                    kmax=max(keep_vals),
                    kmed=median(keep_vals),
                    kavg=(sum(keep_vals)/len(keep_vals)),
                    kmod=mode(keep-vals),
                    # thrown stats
                    tmin=min(throw_vals),
                    tmax=max(throw_vals),
                    tmed=median(throw_vals),
                    tavg=(sum(throw_vals)/len(throw_vals)),
                    tmod=mode(throw_vals))

        session.add(to_add)
        #session.commit()
        return True
    else:
        return False
