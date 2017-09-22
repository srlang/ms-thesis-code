# Sean R. Lang <sean.lang@cs.helsinki.fi>

from sqlalchemy                 import Column, Integer, Float, String
from sqlalchemy                 import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm             import sessionmaker

from config import SQL_ENGINE, SQL_ECHO

engine = create_engine(SQL_ENGINE, echo=SQL_ECHO)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


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

    # Instead let's have the records inserter also update this with a number
    # of the records available (sort of)
    # Keep the same updating as the access_counter, but refresh on this instead
    # N.B. Not an accurate count for the actual number of records
    records_refresh_counter = Column(Integer)
    pass

# No need for special handling anymore
#access_AggregatePlayedHandRecord_counter = 0
#def access_AggregatePlayedHandRecord(cards):
#    global access_AggregatePlayedHandRecord_counter
#    global session
#    # TODO
#    access_AggregatePlayedHandRecord_counter += 1
#    pass

input_PlayedHandRecord_counter = 0
def input_PlayedHandRecord(cards, gained, given):
    '''
    Input a single record for how many points were given/gained from a single
    round of play.
    This will also update the aggregate record for the hands periodically
    according to a power scheme. Every time the floor of the log_2 of the
    counter changes, the aggregate record will be re-polled.
    Because this will cause a lot of records to be ignored for a while after
    the counter increases to only a modest amount, the counter will be reset
    after reaching 128.
    This yields an average refresh rate of 7 refreshes per 128 records, which
    is roughly 1 refresh every 18 records, which is nice from a performance
    perspective, and also avoids the issue of having too little data in the
    beginning phases of the game.
    '''
    global input_PlayedHandRecord_counter
    global session
    record = PlayedHandRecord(
                card0=cards[0],
                card1=cards[1],
                card2=cards[2],
                card3=cards[3],
                score_gained=gained,
                score_given=given)
    session.add(record)

    need_to_add = False
    try:
        agg_rec = session.query(AggregatePlayedHandRecord).filter_by(
                    card0=cards[0],
                    card1=cards[1],
                    card2=cards[2],
                    card3=cards[3]).first()
        if agg_rec is not None:
            # add to counter, potentially refresh
            agg_rec.records_refresh_counter += ((agg_rec.records_refresh_counter + 1)\
                                                    % AGG_REC_REFRESH_MODULO)
            agg_rec.records_refresh_counter = max(agg_rec.records_refresh_counter, 2)
            # refresh if the lower bound power of 2 has changed to refresh 
            #   less as time passes more and more
            if int(log2(agg_rec.records_refresh_counter)) != \
                    int(log2(agg_rec.records_refresh_counter - 1)):
                records = session.query(PlayedHandRecord).filter_by(\
                            card0=cards[0],
                            card1=cards[1],
                            card2=cards[2],
                            card3=cards[3])
                given = [r.score_given for r in records]
                agg_rec.given_min = min(given)
                agg_rec.given_max = max(given)
                agg_rec.given_avg = mean(given)
                agg_rec.given_med = median(given)
                agg_rec.given_mod = mode(given)

                gained = [r.score_gained for r in records]
                agg_rec.gained_min = min(gained)
                agg_rec.gained_max = max(gained)
                agg_rec.gained_avg = mean(gained)
                agg_rec.gained_med = median(gained)
                agg_rec.gained_mod = mode(gained)
                session.commit()
        else:
            need_to_add = True
    except:
        need_to_add = True

    if need_to_add:
        agg_rec = AggregatePlayedHandRecord(
                    card0=cards[0],
                    card1=cards[1],
                    card2=cards[2],
                    card3=cards[3],
                    given_min=given,
                    given_max=given,
                    given_avg=given,
                    given_med=given,
                    given_mod=given,
                    gained_min=gained,
                    gained_max=gained,
                    gained_avg=gained,
                    gained_med=gained,
                    gained_mod=gained,
                    records_refresh_counter=1)
        session.add(agg_rec)
        session.commit()
    input_PlayedHandRecord_counter = (input_PlayedHandRecord_counter + 1) %\
                                        DB_UPDATE_SAVE_INTERVAL_PLAYED_HAND
    if input_PlayedHandRecord_counter == 0:
        try:
            session.commit()
        except InvalidRequestError:
            pass # Do nothing, we've already committed
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
    avg = Column(Integer)
    med = Column(Float)
    mod = Column(Float)
    pass



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

    # Statistics for the kept cards
    kmin = Column(Integer)
    kmax = Column(Integer)
    kmed = Column(Float)
    kavg = Column(Float)
    kmod = Column(Integer)

    # statistics for the thrown cards
    tmin = Column(Integer)
    tmax = Column(Integer)
    tmed = Column(Float)
    tavg = Column(Float)
    tmod = Column(Integer)


def populate_keep_throw_statistics(start_keep=[0, 1, 2, 3], start_throw=[4,5]):
    # TODO: connection stuff
    global session

    # Connect to database
    #session = Session()
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

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
