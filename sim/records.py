# Sean R. Lang <sean.lang@cs.helsinki.fi>

from itertools                  import  combinations
from math                       import  log2

from sqlalchemy                 import  Boolean, Column, Float, Integer, String
from sqlalchemy                 import  create_engine
from sqlalchemy.ext.declarative import  declarative_base
from sqlalchemy.orm             import  sessionmaker

from sqlite3                    import  dbapi2 as sqlite

from statistics                 import  mean, median, mode, StatisticsError

from threading                  import  Thread, Lock



from config                     import  DEBUG,\
                                        DB_ENGINE,\
                                        DB_ECHO,\
                                        DB_UPDATE_SAVE_INTERVAL_AGGPLAYEDHAND,\
                                        DB_UPDATE_SAVE_INTERVAL_PLAYED_HAND,\
                                        DB_POPULATE_SAVE_INTERVAL,\
                                        DB_AGG_REC_REFRESH_MODULO,\
                                        DB_AGGREGATE_REFRESH_MAX
from strategy                   import  _enumerate_possible_hand_values,\
                                        _enumerate_possible_toss_values
from utils                      import  PD

engine = create_engine(DB_ENGINE, echo=DB_ECHO, module=sqlite) #, poolclass=QueuePool)
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


    def hand(self):
        return [self.card0, self.card1, self.card2, self.card3]

    pass

class AggregatePlayedHandRecord(Base):

    '''
    Keep an aggregate record of all accounts of a single 4-card hand that has
    been played.
    Keep this updated regularly.
    This is created to allow the implementation to avoid unnecessary, resource-
    consuming database queries all the time.
    For any instance in which the mode is not unique, the value of x_mod will
    be equivalent to the median simply for ease of use.
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


    def hand(self):
        return [self.card0, self.card1, self.card2, self.card3]

    def generate_id(cards):
        scards = sorted(cards) # double check that things are sorted
        return  scards[0] * 1000000 +\
                scards[1] * 10000 +\
                scards[2] * 100 +\
                scards[3] * 1;

# N.B.:
#   Unfortunately only thought of this well after writing all this,
#   but these records don't take into account the fact that the pone plays
#   first and that the
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
    PD('entering', 'input_PlayedHandRecord')
    global input_PlayedHandRecord_counter
    global session
    scards = sorted(cards)
    record = PlayedHandRecord(
                card0=scards[0],
                card1=scards[1],
                card2=scards[2],
                card3=scards[3],
                score_gained=gained,
                score_given=given)
    session.add(record)

    need_to_add = False
    agg_rec = None
    try:
        PD('> querying for aggregate record', 'input_PlayedHandRecord')
        agg_rec = session.query(AggregatePlayedHandRecord).filter_by(
                    id=AggregatePlayedHandRecord.generate_id(scards)).first()
                    #card0=cards[0],
                    #card1=cards[1],
                    #card2=cards[2],
                    #card3=cards[3]).first() #one_or_none()
    except:
        PD('> Aggregate Record not found, need to create', 'input_PlayedHandRecord')
        need_to_add = True

    PD('> agg_rec=%s' % str(agg_rec), 'input_PlayedHandRecord')
    if agg_rec is not None:
        PD('>> agg_rec has been found', 'input_PlayedHandRecord')
        # add to counter, potentially refresh
        #agg_rec.records_refresh_counter = ((agg_rec.records_refresh_counter + 1)\
        #                                        % DB_AGG_REC_REFRESH_MODULO)
        agg_rec.records_refresh_counter += 1 # ignore
        # ensure log(refresh_counter) and log(refresh_counter-1) exist
        agg_rec.records_refresh_counter = max(agg_rec.records_refresh_counter, 2)
        # refresh if the lower bound power of 2 has changed to refresh 
        #   less as time passes more and more
        PD('agg_rec.records_refresh_counter=%d' % agg_rec.records_refresh_counter,
                'input_PlayedHandRecord')
        if (int(log2(agg_rec.records_refresh_counter)) != \
                int(log2(agg_rec.records_refresh_counter - 1))) or\
                (agg_rec.records_refresh_counter % DB_AGGREGATE_REFRESH_MAX == 0):
                    # include soft limit at (e.g. 100) to override log2 when things are big
            records = session.query(PlayedHandRecord).filter_by(\
                        card0=scards[0],
                        card1=scards[1],
                        card2=scards[2],
                        card3=scards[3])
            given_ = [r.score_given for r in records]
            PD('Updating given stats for hand=%s with given=%s'\
                    % (scards, given_), 'input_PlayedHandRecord')
            agg_rec.given_min = min(given_)
            agg_rec.given_max = max(given_)
            agg_rec.given_avg = mean(given_)
            agg_rec.given_med = median(given_)
            try:
                agg_rec.given_mod = mode(given_)
            except StatisticsError:
                agg_rec.given_mod = agg_rec.given_med

            gained_ = [r.score_gained for r in records]
            PD('Updating given stats for hand=%s with gained=%s'\
                    % (scards, gained_), 'input_PlayedHandRecord')
            agg_rec.gained_min = min(gained_)
            agg_rec.gained_max = max(gained_)
            agg_rec.gained_avg = mean(gained_)
            agg_rec.gained_med = median(gained_)
            try:
                agg_rec.gained_mod = mode(gained_)
            except StatisticsError:
                agg_rec.gained_mod = agg_rec.gained_med
            session.commit()
    else:
        need_to_add = True

    if need_to_add:
        PD('>> need_to_add, creating AggregatePlayedHandRecord object', 'input_PlayedHandRecord')
        agg_rec = AggregatePlayedHandRecord(
                    id=AggregatePlayedHandRecord.generate_id(scards),
                    card0=scards[0],
                    card1=scards[1],
                    card2=scards[2],
                    card3=scards[3],
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
        PD('>> adding new aggregate record to the database', 'input_PlayedHandRecord')
        session.add(agg_rec)
        PD('>> committing transaction', 'input_PlayedHandRecord')
        session.commit()
        PD('>>> transaction commit successful', 'input_PlayedHandRecord')
    input_PlayedHandRecord_counter = (input_PlayedHandRecord_counter + 1) %\
                                        DB_UPDATE_SAVE_INTERVAL_PLAYED_HAND
    PD('> input_PHR_counter=%d' % input_PlayedHandRecord_counter, 'input_PlayedHandRecord')
    if input_PlayedHandRecord_counter == 0:
        PD('>> need to try to commit the transaction', 'input_PlayedHandRecord')
        try:
            session.commit()
            PD('>>> commit successful', 'input_PlayedHandRecord')
        except InvalidRequestError:
            PD('>>> commit unnecessary', 'input_PlayedHandRecord')
            pass # Do nothing, we've already committed
        except Exception as e:
            PD('>>> commit failed: %s' % str(e), 'input_PlayedHandRecord')
    PD('exiting', 'input_PlayedHandRecord')

class RawHandStatistics(Base):

    __tablename__ = 'raw_hands_stats'

    id = Column(Integer, primary_key=True)

    card0 = Column(Integer)
    card1 = Column(Integer)
    card2 = Column(Integer)
    card3 = Column(Integer)

    min = Column(Integer)
    max = Column(Integer)
    avg = Column(Float)
    med = Column(Float)
    mod = Column(Integer)


class KeepThrowStatistics(Base):

    # This table's statistics deal only with the counting phase of the game.
    # Pegging will only be taken into account in its own database table.
    #   This is because pegging is varies so much already that the additional
    #   variance from the thrown cards are not really all that important.

    __tablename__ = 'keep_throw_stats'

    id = Column(Integer, primary_key=True)

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

    #@static_method
    def generate_id(keep, toss):
        skeep = sorted(keep)
        stoss = sorted(toss)
        return  skeep[0] * 10000000000 +\
                skeep[1] * 100000000 +\
                skeep[2] * 1000000 +\
                skeep[3] * 10000 +\
                stoss[0] * 100 +\
                stoss[1] * 1;

def populator_process_method(dealt_hand):
    # Times:
    #   pypy3:
    #       4 Threads:
    #           1:54.82
    #           1:44.16
    #           1:44.99
    #           1:40.45
    #       8 Threads: avg:
    #           1:37.73
    #           1:33.88
    #           1:39.73
    #       16 Threads:
    #           1:39.66
    #           1:37.13
    #           1:37.62
    #           1:47.77
    #   Ukko.pypy3:
    #       16 Threads:
    #           2:08(ish)
    #       32 Threads:
    #           2:07.16
    #           2:02.46
    #   Ukko.pypy3, no database interactions
    #       16 Threads:
    #           2:07.77
    #       32 Threads:
    #           2:00.81
    METHOD = 'populator_process_method(%s)' % str(dealt_hand)
    PD('entering', METHOD)
    eng = create_engine(DB_ENGINE, echo=DB_ECHO, module=sqlite)
    _Se = sessionmaker(bind=engine)
    sess = _Se()
    total_done = 0
    increased = 0
    failed = 0
    for keep in combinations(dealt_hand, 4):
        k = list(keep)
        t = [card for card in dealt_hand if card not in k]
        total_done += 1
        try:
            if total_done % 10 == 0:
                PD('> working on (k,t)=(%s,%s)' % (str(k),str(t)), METHOD)
            inc = _populate_keep_throw_statistics(k, t, sess)
            inc = True
            increased += 1 if inc else 0
        except Exception as e:
            PD('> Exception: %s' % str(e), METHOD)
            failed += 1
            pass
    PD('committing transaction')
    try:
        sess.commit()
    except InvalidRequestError:
        pass
    except Exception as e:
        PD('> exception: ' + str(e), METHOD)
    PD('exiting', METHOD)

class PopulatorThread(Thread):

    def __init__(self, _id):
        Thread.__init__(self)
        self._id = _id
        self.engine = create_engine(DB_ENGINE, echo=DB_ECHO, module=sqlite)
        _Session = sessionmaker(bind=engine)
        self.session = _Session()

    def run(self):
        METHOD = 'Populator.run(%d)' % self._id
        PD('Entering', METHOD)
        increased = 0
        failed = 0
        total_done = 0
        kt = _multithreaded_delegator()
        while kt is not None:
            for keep in combinations(kt, 4):
                k = list(keep)
                t = [card for card in kt if card not in k]
                total_done += 1
                try:
                    if total_done % 100 == 0:
                        PD('> working on (k,t)=(%s,%s)' % (str(k),str(t)), METHOD)
                    inc = _populate_keep_throw_statistics(k, t, self.session)
                    #inc = True
                    increased += 1 if inc else 0
                except Exception as e:
                    PD('> Exception: %s' % str(e), METHOD)
                    failed += 1
            #PD('> getting next dealt hand', METHOD)
            kt = _multithreaded_delegator()
        PD('Finished total:%d, increased:%d, failed:%d' % (total_done, increased, failed), METHOD)
        PD('committing transactions', METHOD)
        try:
            self.session.commit()
        except InvalidRequestError:
            pass
        except Exception as e:
            PD('exception: ' + str(e), METHOD)
        self.session.close()
        PD('exiting', METHOD)


def populate_keep_throw_statistics_multithreaded(num_threads=8):
    # Interlude method to get around the issue of speed of database populating
    PD('entering', 'pop_multi')

    dealt_possibilities = combinations(range(52), 6)
    if DEBUG:
        dealt_possibilities = combinations(range(10), 6)

    threads = []
    for i in range(num_threads):
        thread = PopulatorThread(i)
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    PD('exiting', 'pop_multi')
    pass

delegator_combinations_lock = Lock()
delegator_combinations = None
def _multithreaded_delegator():
    global delegator_combinations
    global delegator_combinations_index
    global delegator_combinations_index_lock
    METHOD = '_multithreaded_delegator'

    ret = None
    #PD('> acquiring lock', METHOD)
    delegator_combinations_lock.acquire()
    try:
        ret = delegator_combinations.__next__()
    except StopIteration:
        pass
    #PD('> releasing lock', METHOD)
    delegator_combinations_lock.release()

    #PD('> exiting with ret=' + str(ret), METHOD)
    return ret



def populate_keep_throw_statistics(start_keep=[0, 1, 2, 3], start_throw=[4,5]):
    # Still is a very slow operation
    #   According to my manual timing, 10 new records can be inserted in
    #   roughly 6.4 seconds.
    #   At this speed, it would take 150 days to populate just this database
    #   table.
    # N.B.: ask Dr. Roos for directions at this point
    #  options:
    #   1: run RIGHT NOW and still have 6 months wait (guess)
    #   2: rewrite population code (and scoring) into a lower-level, more
    #       parallelizable language
    #   3: take that performance hit when we are dealt each hand?
    global session
    PD('entering', 'populate_keep_throw_statistics')

    PD('> enumerating all possible keep,throw possibilities for all hands...',
            'populate_keep_throw_statistics')
    poss_hands = combinations(range(52), 6)
    if DEBUG:
        poss_hands = combinations(range(10), 6)
    # hard code 52 c 6
    PD('>> num possible dealt hands=%d' % 20358520, 'populate_keep_throw_statistics')
    possible_keep_throws = []
    for hand in poss_hands:
        PD('>>> dealing with hand: %s' % str(hand), 'populate_keep_throw_statistics')
        keeps = combinations(hand, 4)
        for keep in keeps:
            throw = [c for c in hand if c not in keep]
            possible_keep_throws.append((list(keep), list(throw)))
    total = len(possible_keep_throws)
    PD('> enumerating done (%d total)' % total,
            'populate_keep_throw_statistics')

    # Find keep/throw possibilities
    # Run through possibilities
    failed = 0
    increased = 0
    PD('> running through keep,throw possibilities', 'populate_keep_throw_statistics')
    for keep,throw in possible_keep_throws:
        PD('>> trying to insert keep=%s, throw=%s' % (keep, throw),
                'populate_keep_throw_statistics')
        try:
            PD('>>> calling _populate_keep_throw_statistics', 'populate_keep_throw_statistics')
            inc = _populate_keep_throw_statistics(keep, throw)
            PD('>>>> returned success=%s' % inc, 'populate_keep_throw_statistics')
            increased += 1 if inc else 0
            if increased % DB_POPULATE_SAVE_INTERVAL == 0:
                PD('>>>>> increased enough to commit', 'populate_keep_throw_statistics')
                # commit transactions every so often to avoid unnecessary
                # slowing down but also avoid losing all progress due to some
                # stupid error occurring midway
                session.commit()
            PD('>>> "succeeded"', 'populate_keep_throw_statistics')
        except Exception as e:
            # Database interaction failed
            PD('>>> FAILED!!! (%s)' % str(e), 'populate_keep_throw_statistics')
            failed += 1
    PD('> ending the population stage with %d inserted of %d total, %d failed' % \
            (increased, total, failed),
            'populate_keep_throw_statistics')

    # make sure to commit all pending transactions at the end of insertions
    try:
        PD('> committing', 'populate_keep_throw_statistics')
        session.commit()
        PD('>> successful', 'populate_keep_throw_statistics')
    except InvalidRequestError:
        PD('>> unnecessary', 'populate_keep_throw_statistics')
    except Exception as e:
        PD('>> failed (%s)' % str(e), 'populate_keep_throw_statistics')


database_interaction_lock = Lock()
def _populate_keep_throw_statistics(keep, throw, sess):
    # Populate the individual keep/throw possibility with all statistics
    # as desired.
    # Dumb method. No handling of any exceptions, etc.
    #database_interaction_lock.acquire()
    with sess.no_autoflush:
        found_data = sess.query(KeepThrowStatistics).filter_by(\
                        id=KeepThrowStatistics.generate_id(keep,throw)).first()
                        #kcard0=keep[0],
                        #kcard1=keep[1],
                        #kcard2=keep[2],
                        #kcard3=keep[3],
                        #tcard0=throw[0],
                        #tcard1=throw[1]).first() #one_or_none()
    #database_interaction_lock.release()
    if found_data is None:
        # Calculate statistics and add to database

        # Calculate statistics
        keep_vals = _enumerate_possible_hand_values(keep, throw)
        throw_vals = _enumerate_possible_toss_values(keep, throw)

        add_KeepThrowStatistic(keep, throw, keep_vals, throw_vals, sess)
        #session.commit()
        return True
    else:
        return False

def add_KeepThrowStatistic(keep, throw, keep_vals, throw_vals, sess):
        # add new row to database
        kmed = median(keep_vals)
        kmod = kmed
        try:
            kmod = mode(keep_vals)
        except StatisticsError:
            kmod = kmed
        tmed = median(throw_vals)
        tmod = tmed
        try:
            tmod = mode(throw_vals)
        except StatisticsError:
            tmod = tmed

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
                    kmed=kmed,
                    kavg=mean(keep_vals),
                    kmod=kmod,
                    # thrown stats
                    tmin=min(throw_vals),
                    tmax=max(throw_vals),
                    tmed=tmed,
                    tavg=mean(throw_vals),
                    tmod=tmod)

        #database_interaction_lock.acquire()
        sess.add(to_add)
        #database_interaction_lock.release()

class PlayedRoundRecord(Base):

    '''
    Not entirely sure I want to do this.
    Do I want to adjust weights of each strategy, or keep track of their actual
    performance and decide based on that?
    N.B.: Ask Dr. Roos
    '''

    __tablename__ = 'played_round'

    id = Column(Integer, primary_key=True)


    my_score = Column(Integer)
    opp_score = Column(Integer)
    am_dealer = Column(Boolean)

    score_gained = Column(Integer)
    score_given = Column(Integer)


class StrategyRecord(Base):

    __tablename__ = 'strategy'

    id = Column(Integer, primary_key=True)

    my_score = Column(Integer)
    opp_score = Column(Integer)
    am_dealer = Column(Boolean)

    # Percentage of "confidence" in each strategy
    # Otherwise interpreted as the percentage in which strategy s should be
    #   chosen at this stage in the game
    strategy_a = Column(Float)
    strategy_b = Column(Float)
    strategy_c = Column(Float)

    def reward(self, strategy):
        # TODO
        # Reward a strategy for good results by increasings its percentage of
        #   being chosen at this point (and decreasing others')
        # TODO
        pass

    def penalize(self, strategy):
        # TODO
        # Penalize a strategy for poor results by lowering its percentage
        #   chance of being picked (and boosting others')
        # TODO
        pass


def main_populate():
    global delegator_combinations
    create_tables()
    delegator_combinations = combinations(range(10), 6)
    #populate_keep_throw_statistics_multithreaded()
    from multiprocessing import Pool
    with Pool(processes=4) as pool:
        pool.map(populator_process_method, delegator_combinations)

def main_create():
    print('running creation mode only')
    create_tables()
    session.commit()

if __name__ == '__main__':
    from sys import argv
    if len(argv) > 1 and argv[1] != '--create':
        db_file = argv[1]
        l_engine = DB_ENGINE_PREFIX + db_file
        engine = create_engine(l_engine, echo=DB_ECHO, module=sqlite)
        Session = sessionmaker(bind=engine)
        session = Session()
    if '--create' in argv:
        main_create()
    else:
        main_populate()
