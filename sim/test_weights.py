# Sean R. Lang <sean.lang@cs.helsinki.fi>

from weights            import * #WeightCoordinate, create_weight_tables

from sqlalchemy         import create_engine
from sqlalchemy.orm     import sessionmaker

local_engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=local_engine)
local_sess = None #Session()

_db_setup_run = False
_db_setup_suc = False
def db_setup():
    # doubles as test_create_weight_tables
    global _db_setup_run
    global _db_setup_suc
    global local_sess
    global local_engine
    global Session
    if (not _db_setup_run) and (not _db_setup_suc):
        local_sess = Session()
        create_weight_tables(local_engine)
        wcs = [
                WeightCoordinate(my_score=12, opp_score=13, dealer=False, w0=1, w1=3, w2=2),
                WeightCoordinate(my_score=17, opp_score=11, dealer=True, w0=0, w1=2, w2=3),
                WeightCoordinate(my_score=11, opp_score=12, dealer=False, w0=2, w1=1, w2=4)
                ]
        for wc in wcs:
            local_sess.add(wc)
        local_sess.commit()
        _db_setup_run = True
        _db_setup_suc = local_sess is not None and \
                (local_sess.query(WeightCoordinate).first() is not None)


def test_read_weights():
    global local_sess
    db_setup()

    wc0 = read_weights(local_sess, 12, 13, False) #, 3)
    #wc00 = read_weights(local_sess, 12, 13, False, 2)
    wc1 = read_weights(local_sess, 17, 11, True) #, 3)
    wc2 = read_weights(local_sess, 11, 12, False) #, 3)
    assert wc0 is not None
    #assert wc00 is not None
    assert wc1 is not None
    assert wc2 is not None
    assert wc0.w0 == 1 and wc0.w1 == 3 and wc0.w2 == 2

def test_to_str():
    wc0 = WeightCoordinate(my_score=10, opp_score=12, dealer=True, w0=1, w1=2, w2=4)
    wc1 = WeightCoordinate(my_score=10, opp_score=12, dealer=False, w0=3, w1=2, w2=1)
    assert wc0.to_str(3) == '10 12 1 1 2 4'
    assert wc1.to_str(3) == '10 12 0 3 2 1'

def test_weights():
    wc0 = WeightCoordinate(my_score=10, opp_score=12, dealer=True, w0=1, w1=2, w2=4)
    wc1 = WeightCoordinate(my_score=10, opp_score=12, dealer=True, w0=3, w1=2, w2=1)
    assert wc0.weights(3) == [1,2,4]
    assert wc0.weights(2) == [1,2]
    assert wc1.weights(1) == [3]
    assert wc1.weights(3) == [3, 2, 1]

