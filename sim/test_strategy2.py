# Sean R. Lang

from strategy2 import   *
from strategy2 import   _possible_keep_toss_tuple_list,\
                        _retrieve_hand_statistics,\
                        _retrieve_property_list,\
                        _get_all_indices,\
                        _get_by_multiple_indices,\
                        _to_keep_toss_tuple

_setup_run = False
_setup_suc = False
def db_setup():
    global _setup_run
    global _setup_suc
    if (not _setup_run) and (not _setup_suc):
        # populate with basic stuff for the first few cards
        PD('need to run')
        l_succ = True 
        from records import _populate_keep_throw_statistics, session, KeepThrowStatistics
        cards_l = [
                    [0, 1, 2, 3, 4, 5]
                    ]
        for cards in cards_l:
            for keep in combinations(cards, 4):
                k = list(keep)
                t = [card for card in cards if card not in k]
                PD('populating keep=%s, toss=%s' % (k,t))
                try:
                    #l_succ = l_succ and
                    _populate_keep_throw_statistics(k,t, session)
                    session.commit()
                except Exception as e:
                    PD('error: %s' % str(e))
                    l_succ = False

        # populate with non-existant cards so that it can be consistent when
        # dealing with pegging choices
        pcards_l = [
                    [60, 61, 62, 63, 64, 65]
                    ]

        _setup_run = True
        l_succ = l_succ and session.query(KeepThrowStatistics).filter_by(\
                            kcard0=cards_l[0][0],
                            kcard1=cards_l[0][1],
                            kcard2=cards_l[0][2],
                            kcard3=cards_l[0][3],
                            tcard0=cards_l[0][4],
                            tcard1=cards_l[0][5]).first() is not None
        _setup_suc = l_succ




#def test_db_setup():
#    global _setup_run
#    global _setup_suc
#    assert not _setup_run
#    assert not _setup_suc
#    db_setup()
#    assert _setup_run
#    assert _setup_suc


def test__possible_keep_toss_tuple_list():
    cards = [0, 1, 2, 3, 4, 5]
    combos = [
                ((0, 1, 2, 3), (4, 5)),
                ((0, 1, 2, 4), (3, 5)),
                ((0, 1, 2, 5), (3, 4)),
                ((0, 1, 3, 4), (2, 5)),
                ((0, 1, 3, 5), (2, 4)),
                ((0, 1, 4, 5), (2, 3)),
                ((0, 2, 3, 4), (1, 5)),
                ((0, 2, 3, 5), (1, 4)),
                ((0, 2, 4, 5), (1, 3)),
                ((0, 3, 4, 5), (1, 2)),
                ((1, 2, 3, 4), (0, 5)),
                ((1, 2, 3, 5), (0, 4)),
                ((1, 2, 4, 5), (0, 3)),
                ((1, 3, 4, 5), (0, 2)),
                ((2, 3, 4, 5), (0, 1))
                ]
    poss_kt_tl = _possible_keep_toss_tuple_list(cards)
    for kt in poss_kt_tl:
        assert kt in combos
    for combo in combos:
        assert combo in poss_kt_tl

def test__retrieve_hand_statistics():
    db_setup()
    keep = (0, 1, 2, 3)
    toss = (4, 5)
    kts = _retrieve_hand_statistics((keep,toss)) #, session=session)
    assert kts is not None
    assert kts.kcard0 == 0
    assert kts.kcard1 == 1
    assert kts.kcard2 == 2
    assert kts.kcard3 == 3
    assert kts.tcard0 == 4
    assert kts.tcard1 == 5

def test_possible_KeepThrowStatistics():
    cards = [0, 1, 2, 3, 4, 5]
    combos = [
                ((0, 1, 2, 3), (4, 5)),
                ((0, 1, 2, 4), (3, 5)),
                ((0, 1, 2, 5), (3, 4)),
                ((0, 1, 3, 4), (2, 5)),
                ((0, 1, 3, 5), (2, 4)),
                ((0, 1, 4, 5), (2, 3)),
                ((0, 2, 3, 4), (1, 5)),
                ((0, 2, 3, 5), (1, 4)),
                ((0, 2, 4, 5), (1, 3)),
                ((0, 3, 4, 5), (1, 2)),
                ((1, 2, 3, 4), (0, 5)),
                ((1, 2, 3, 5), (0, 4)),
                ((1, 2, 4, 5), (0, 3)),
                ((1, 3, 4, 5), (0, 2)),
                ((2, 3, 4, 5), (0, 1))
                ]
    pass

def test__retrieve_property_list():
    kts = [
            KeepThrowStatistics(kcard0=12, kcard1=23, kcard2=33, kcard3=40), #, tcard0=2, tcard1=3)
            KeepThrowStatistics(kcard0=11, kcard1=22, kcard2=33, kcard3=44),
            KeepThrowStatistics(kcard0=12, kcard1=23, kcard2=34, kcard3=45),
            ]
    props = _retrieve_property_list(kts, 'kcard1')
    assert props == [23, 22, 23]

def test__get_all_indices():
    lst = [1, 1, 2, 3, 5, 8]
    assert _get_all_indices(lst, 1) == [0, 1]
    assert _get_all_indices(lst, 2) == [2]
    lst = [1, 1, 1, 1, 1, 2]
    assert _get_all_indices(lst, 1) == [0, 1, 2, 3, 4]
    lst = [1, 1, 1, 2, 1, 2]
    assert _get_all_indices(lst, 1) == [0, 1, 2, 4]

def test__get_by_multiple_indices():
    tlist = range(10)
    assert _get_by_multiple_indices(tlist, [0, 1, 3]) == [0, 1, 3]
    assert _get_by_multiple_indices(tlist, [0, 3, 5]) == [0, 3, 5]
    assert _get_by_multiple_indices(tlist, [0, 2, 8]) == [0, 2, 8]
    assert _get_by_multiple_indices(tlist, [0, 8, 3]) == [0, 8, 3]

def  test__to_keep_toss_tuple():
    kts = KeepThrowStatistics(kcard0=1,
            kcard1=2,
            kcard2=3,
            kcard3=4,
            tcard0=0,
            tcard1=5,
            kmin=0,
            kmax=29,
            kmed=22,
            kavg=21,
            kmod=12,
            tmin=0,
            tmax=29,
            tmed=22,
            tavg=21,
            tmod=12)
    assert _to_keep_toss_tuple(kts) == ((1,2,3,4),(0,5))

###def test_hand_picker():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    exp_max_min = [((0, 1, 2, 3), (4, 5))]
###    exp_min_min = [((0, 1, 4, 5), (2, 3)),
###                    ((0, 2, 4, 5), (1, 3)),
###                    ((0, 3, 4, 5), (1, 2)),
###                    ((1, 2, 4, 5), (0, 3)),
###                    ((1, 3, 4, 5), (0, 2)),
###                    ((2, 3, 4, 5), (0, 1))]
###    assert exp_max_min == hand_picker(cards, 'kmin', max)
###    # impractical, but good proof of functionality
###    assert exp_min_min == hand_picker(cards, 'kmin', min)
###
###def test_hand_max_min():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    exp_max_min = [((0, 1, 2, 3), (4, 5))]
###    assert exp_max_min == hand_max_min(cards)
###
###def test_hand_max_avg():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    exp = [((0, 1, 2, 3), (4, 5))]
###    assert exp == hand_max_avg(cards)
###
###def test_hand_max_med():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    exp = [((0, 1, 2, 3), (4, 5))]
###    assert exp == hand_max_med(cards)
###
###def test_hand_max_poss():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    exp = [((0, 1, 2, 3), (4, 5))]
###    assert exp == hand_max_poss(cards)
###
###def test_hand_min_avg_crib():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    #exp = [((0, 1, 2, 3), (4, 5))]
###    #assert exp == hand_min_avg_crib(cards)
####    exp = [
####            ((1, 2, 3, 4), (0, 5)),
####            ((0, 1, 2, 4), (1, 5)),
####            ((0, 1, 3, 4), (2, 5)),
####            ((0, 1, 3, 5), (2, 4))
####            ]
###    exp = [
###            ((0, 1, 2, 4), (3, 5)),
###            ((0, 1, 2, 5), (3, 4)),
###            ((0, 1, 3, 4), (2, 5)),
###            ((0, 1, 3, 5), (2, 4)),
###            ((0, 2, 3, 5), (1, 4)),
###            ((1, 2, 3, 4), (0, 5))
###            ]
###    act = hand_min_avg_crib(cards)
###    for e in exp:
###        assert e in act
###    for a in act:
###        assert a in exp
###
####def test_hand_max_avg_both():
####    db_setup()
####    cards = [0, 1, 2, 3, 4, 5]
####    assert False
####    pass
###
####
#### How should I handle the pegging methods?
####   debug database?
####   prepopulate with non-existant cards?
####
###def test_pegging_max_avg_gained():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    assert False
###    pass
###
###def test_pegging_max_med_gained():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    assert False
###    pass
###
###def test_pegging_min_avg_given():
###    db_setup()
###    cards = [0, 1, 2, 3, 4, 5]
###    assert False
###    pass
###
