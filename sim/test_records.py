# Sean R. Lang <sean.lang@cs.helsinki.fi>


from utils import PD

from records import *
from records import _populate_keep_throw_statistics

def test_input_PlayedHandRecord():
    create_tables()
    session.query(PlayedHandRecord).delete()
    session.query(AggregatePlayedHandRecord).delete()

    hand = [0, 1, 2, 3]
    # indices:0  1  2  3  4  5  6  7  8
    # agg_ctr:2  3  4  5  6  7  8  9  10
    # refresh:1  0  1  0  0  0  1  0  0
    gained = [3, 3, 4, 2, 1, 4, 6, 3, 4]
    given  = [2, 4, 3, 4, 6, 1, 2, 3, 2]

    # insert 1 to make sure it's there at all
    input_PlayedHandRecord(hand, gained=gained[0], given=given[0])
    try:
        # make sure the record is present in the database
        record = session.query(PlayedHandRecord).one_or_none()
        assert record.score_gained == gained[0]
        assert record.score_given == given[0]
        assert record.hand() == hand

        # make sure the aggregate record is created
        agg_rec = session.query(AggregatePlayedHandRecord).one_or_none()
        assert agg_rec.hand() == hand
        assert agg_rec.gained_min == agg_rec.gained_max == gained[0]
        assert agg_rec.given_min == agg_rec.given_max == given[0]
    except Exception as e:
        print(e)
        print(str(e))
        assert False

    # insert the rest of the records
    for i in range(1, len(gained)):
        input_PlayedHandRecord(hand, gained=gained[i], given=given[i])

    try:
        # make sure the record is present in the database
        records = session.query(PlayedHandRecord)
        assert records.count() == len(given)

        # make sure the aggregate record is created
        agg_rec = session.query(AggregatePlayedHandRecord).first()
        assert agg_rec.hand() == hand
        PD('agg_rec.__dict__=%s' % str(agg_rec.__dict__), 'test_input__')
        # N.B.: not entirely sure why 8 is this magic number, but important
        #       part is that the updating happens at the logarithmic rate
        given_ = given[:8]
        assert agg_rec.given_min == min(given_)
        assert agg_rec.given_max == max(given_)
        assert agg_rec.given_avg == sum(given_) / len(given_)
        gained_ = gained[:8]
        assert agg_rec.gained_min == min(gained_)
        assert agg_rec.gained_max == max(gained_)
        assert agg_rec.gained_avg == sum(gained_) / len(gained_)
    except Exception as e:
        print(e)
        print(str(e))
        assert False

def test__populate_keep_throw_statistics():
    # ensure created database and wipe table for testing purposes
    create_tables()
    session.query(KeepThrowStatistics).delete()

    keep = [0, 1, 2, 3]
    toss = [5, 6]
    try:
        PD('prelim query to ensure empty before population')
        q = session.query(KeepThrowStatistics).filter_by(\
                kcard0=keep[0],
                kcard1=keep[1],
                kcard2=keep[2],
                kcard3=keep[3],
                tcard0=toss[0],
                tcard1=toss[1])
        assert q.count() == 0
        assert _populate_keep_throw_statistics(keep, toss, session)
        PD('query again to make sure inserted object is present')
        q = session.query(KeepThrowStatistics).filter_by(\
                kcard0=keep[0],
                kcard1=keep[1],
                kcard2=keep[2],
                kcard3=keep[3],
                tcard0=toss[0],
                tcard1=toss[1])
        assert q.count() == 1
        kts = q.one_or_none()
        assert kts.kmin == 12
        assert kts.kmax == 12
        assert kts.kavg == 12
    except Exception as e:
        PD('Error: %s' % str(e))
        assert False

def test_populate_keep_throw_statistics():
    # Untestable unless I figure out a way to make the method have a start/end
    # point.
    #assert False
    pass

def test_KeepThrowStatistics_generate_id():
    id_ = KeepThrowStatistics.generate_id
    assert id_([1,2,3,4], [5,6]) == 10203040506
    assert id_([10,2,3,4], [11,22]) == 100203041122
    assert id_([10,12,14,15],[0, 2]) == 101214150002


if __name__ == '__main__':
    #test_input_PlayedHandRecord()
    test_KeepThrowStatistics_generate_id()
