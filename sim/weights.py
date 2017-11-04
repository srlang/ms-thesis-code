# Sean R. Lang <sean.lang@cs.helsinki.fi>

'''
Keep track of weights independently for each agent object instantiation.
'''

from sqlalchemy                 import  Boolean, Column, Float, Integer, String
from sqlalchemy.ext.declarative import  declarative_base

Base = declarative_base()


def create_weight_tables(db_engine):
    global Base
    Base.metadata.create_all(db_engine)


def read_weights(db_sess, my_score, opp_score, dealer): #, num_weights):
    record = db_sess.query(WeightCoordinate).filter_by(\
                my_score=my_score,
                opp_score=opp_score,
                dealer=dealer).first()
    return record
#    if record is not None:
#        #return [record.__dict__['w%d' % i] for i in range(num_weights)]   
#        return record.weights(num_weights)
#    else:
#        return [0.0] * num_weights


class WeightDeclaration(Base):

    __tablename__ = 'weight_declaration'

    id = Column(Integer, primary_key=True)

    num_strats = Column(String)

    strat0 = Column(String)
    strat1 = Column(String)
    strat2 = Column(String)
    strat3 = Column(String)
    strat4 = Column(String)
    strat5 = Column(String)
    strat6 = Column(String)
    strat7 = Column(String)
    strat8 = Column(String)
    strat9 = Column(String)
    strat10 = Column(String)
    strat11 = Column(String)
    strat12 = Column(String)
    strat13 = Column(String)
    strat14 = Column(String)


class WeightCoordinate(Base):

    __tablename__ = 'weight_coordinate'

    id = Column(Integer, primary_key=True)

    my_score = Column(Integer)
    opp_score = Column(Integer)
    dealer = Column(Boolean)

    w0 = Column(Float)
    w1 = Column(Float)
    w2 = Column(Float)
    w3 = Column(Float)
    w4 = Column(Float)
    w5 = Column(Float)
    w6 = Column(Float)
    w7 = Column(Float)
    w8 = Column(Float)
    w9 = Column(Float)
    w10 = Column(Float)
    w11 = Column(Float)
    w12 = Column(Float)
    w13 = Column(Float)
    w14 = Column(Float)

    def weights(self, num):
        # retrieve the number of weights desired
        return [self.__dict__['w%d' % i] for i in range(num)]

    def to_str(self, num):
        weights_list = [self.__dict__['w%d'%i] for i in range(num)]
        weights_list_str = ' '.join([str(w) for w in weights_list])
        coords_str = '%d %d %d ' % (self.my_score, self.opp_score,self.dealer)
        return coords_str + weights_list_str

