# Sean R. Lang <sean.lang@cs.helsinki.fi>

from strategy3  import *
from strategy3  import _retrieve_property_list
from records    import _populate_keep_throw_statistics,\
                        session as records_session,\
                        KeepThrowStatistics,\
                        AggregatePlayedHandRecord


_setup_run = False
_setup_suc = False
def db_setup():
    global records_session
    global _setup_run
    global _setup_suc
    if (not _setup_run) and (not _setup_suc):
        # populate with basic stuff for the first few cards
        PD('need to run')
        l_succ = True 
        cards_l = [
                    [0, 1, 2, 3, 4, 5],
                    [60, 61, 62, 63, 64, 65]
                    ]
        for cards in cards_l:
            for keep in combinations(cards, 4):
                k = list(keep)
                t = [card for card in cards if card not in k]
                PD('populating keep=%s, toss=%s' % (k,t))
                try:
                    #l_succ = l_succ and
                    _populate_keep_throw_statistics(k,t, records_session)
                    records_session.commit()
                except Exception as e:
                    PD('error: %s' % str(e))
                    l_succ = False

        # populate with non-existant cards so that it can be consistent when
        # dealing with pegging choices
        pcards_l = [
                    ([60, 61, 62, 63], [2, 14, 4.3, 5.1, 4]),
                    ([61, 62, 63, 64], [2, 14, 4.3, 5.1, 4]),
                    ([62, 63, 64, 65], [2, 14, 4.3, 5.1, 4])
                    ]

        for pcards,stats in pcards_l:
            aggrec = AggregatePlayedHandRecord(\
                        card0=pcards[0],
                        card1=pcards[1],
                        card2=pcards[2],
                        card3=pcards[3],
                        gained_min=stats[0],
                        gained_max=stats[1],
                        gained_avg=stats[2],
                        gained_med=stats[3],
                        gained_mod=stats[4],
                        given_min=stats[0],
                        given_max=stats[1],
                        given_avg=stats[2],
                        given_med=stats[3],
                        given_mod=stats[4],
                        records_refresh_counter=1)
            try:
                records_session.add(aggrec)
                records_session.commit()
            except Exception as e:
                PD('error: %s' % str(e))

        _setup_run = True
        l_succ = l_succ and records_session.query(KeepThrowStatistics).filter_by(\
                            kcard0=cards_l[0][0],
                            kcard1=cards_l[0][1],
                            kcard2=cards_l[0][2],
                            kcard3=cards_l[0][3],
                            tcard0=cards_l[0][4],
                            tcard1=cards_l[0][5]).first() is not None
        l_succ = l_succ and records_session.query(AggregatePlayedHandRecord).filter_by(\
                            card0=pcards_l[0][0][0],
                            card1=pcards_l[0][0][1],
                            card2=pcards_l[0][0][2],
                            card3=pcards_l[0][0][3]).first() is not None
        _setup_suc = l_succ



### Passing as of Oct 27th 15:34
###def test_db_setup():
###    #from records import session, KeepThrowStatistics,
###    global _setup_run
###    global _setup_suc
###    assert not _setup_run
###    assert not _setup_suc
###    db_setup()
###    assert _setup_run
###    assert _setup_suc
###    assert records_session.query(KeepThrowStatistics).first() is not None
###    assert records_session.query(AggregatePlayedHandRecord).first() is not None

def test__retrieve_property_list():
    db_setup()
    # with KeepThrowStatistics
    kts = [
            KeepThrowStatistics(kmin=33, kmax=23),
            KeepThrowStatistics(kmin=12, kmax=21),
            KeepThrowStatistics(kmin=10, kmax=20)
            ]
    aphrs = [
            AggregatePlayedHandRecord(card0=0, card1=23),
            AggregatePlayedHandRecord(card0=2, card1=12),
            AggregatePlayedHandRecord(card0=3, card1=22)
            ]

    # with AggregatePlayedHandRecord
    assert _retrieve_property_list(kts, 'kmin') == [33, 12, 10]
    assert _retrieve_property_list(kts, 'kmax') == [23, 21, 20]
    assert _retrieve_property_list(aphrs, 'card0') == [0, 2, 3]
    assert _retrieve_property_list(aphrs, 'card1') == [23, 12, 22]

def test_kts_evaluator():
    kts = [
            KeepThrowStatistics(kmin=0),
            KeepThrowStatistics(kmin=5),
            KeepThrowStatistics(kmin=10)
            ]
    # min = True
    assert kts_evaluator(kts, 'kmin', min_=True) == [1.0, 0.5, 0.0]
    # min = False
    assert kts_evaluator(kts, 'kmin', min_=False) == [0.0, 0.5, 1.0]

def test_pegging_evaluator():
    aphrs = [
            AggregatePlayedHandRecord(given_min=0),
            AggregatePlayedHandRecord(given_min=8),
            AggregatePlayedHandRecord(given_min=16)
            ]

    # with AggregatePlayedHandRecord
    assert kts_evaluator(aphrs, 'given_min', min_=True) == [1.0, 0.5, 0.0]
    assert kts_evaluator(aphrs, 'given_min', min_=False) == [0.0, 0.5, 1.0]

def test_possible_AggregatePlayedHandRecords():
    db_setup()
    # given ktts = list[(keep,toss)]
    ktts = [
            ((61,62,63,64), (0,0)),
            ((62,63,64,65), (0,0)),
            ((60,61,62,63), (0,0))
            ]
    retrieved = possible_AggregatePlayedHandRecords(ktts)
    assert len(retrieved) == len(ktts)
    for ar in retrieved:
        assert ar is not None
        assert ((ar.card0, ar.card1, ar.card2, ar.card3), (0,0)) in ktts

def test_possible_KeepThrowStatistics():
    # FAILING
    db_setup()
    ktts = [
            ((60,61,62,63), (64,65)),
            ((61,62,63,64), (60,65)),
            ((62,63,64,65), (60,61))
            ]
    retrieved = possible_KeepThrowStatistics(ktts)
    assert len(retrieved) == len(ktts)
    for k in retrieved:
        assert k is not None
        assert ((k.kcard0, k.kcard1, k.kcard2, k.kcard2), (k.tcard0, k.tcard1)) in ktts

def test_hand_evaluator():
    # FAILING
    cards = [0, 1, 2, 3, 4, 5]
    assert [[],[]] == hand_evaluator(cards, [hand_max_min, hand_max_poss])

def test_hand_max_min():
    kts = [
            KeepThrowStatistics(kmin=0),
            KeepThrowStatistics(kmin=5),
            KeepThrowStatistics(kmin=10)
            ]
    assert hand_max_min(kts) == [0.0, 0.5, 1.0]

def test_hand_max_avg():
    kts = [
            KeepThrowStatistics(kavg=0),
            KeepThrowStatistics(kavg=5),
            KeepThrowStatistics(kavg=10)
            ]
    assert hand_max_avg(kts) == [0.0, 0.5, 1.0]

def test_hand_max_med():
    kts = [
            KeepThrowStatistics(kmed=0),
            KeepThrowStatistics(kmed=5),
            KeepThrowStatistics(kmed=10)
            ]
    assert hand_max_med(kts) == [0.0, 0.5, 1.0]

def test_hand_max_poss():
    kts = [
            KeepThrowStatistics(kmax=0),
            KeepThrowStatistics(kmax=5),
            KeepThrowStatistics(kmax=10)
            ]
    assert hand_max_poss(kts) == [0.0, 0.5, 1.0]

def test_hand_max_min():
    kts = [
            KeepThrowStatistics(kmin=0),
            KeepThrowStatistics(kmin=5),
            KeepThrowStatistics(kmin=10)
            ]
    assert hand_max_min(kts) == [0.0, 0.5, 1.0]

def test_crib_min_avg():
    kts = [
            KeepThrowStatistics(tavg=0),
            KeepThrowStatistics(tavg=5),
            KeepThrowStatistics(tavg=10)
            ]
    assert crib_min_avg(kts) == [1.0, 0.5, 0.0]

def test_pegging_max_avg_gained():
    aphrs = [
            AggregatePlayedHandRecord(gained_avg=0),
            AggregatePlayedHandRecord(gained_avg=5),
            AggregatePlayedHandRecord(gained_avg=10)
            ]
    assert pegging_max_avg_gained(None, aphrs) == [0.0, 0.5, 1.0]

def test_pegging_max_med_gained():
    aphrs = [
            AggregatePlayedHandRecord(gained_med=0),
            AggregatePlayedHandRecord(gained_med=5),
            AggregatePlayedHandRecord(gained_med=10)
            ]
    assert pegging_max_med_gained(None, aphrs) == [0.0, 0.5, 1.0]

def test_pegging_min_avg_given():
    aphrs = [
            AggregatePlayedHandRecord(given_avg=0),
            AggregatePlayedHandRecord(given_avg=5),
            AggregatePlayedHandRecord(given_avg=10)
            ]
    assert pegging_min_avg_given(None, aphrs) == [1.0, 0.5, 0.0]

