import os
#import requests_mock
#from utils.settings import settings
#from pathlib import Path
from .balance import get_wallet
from .sim import get_sim_details
from .subscriptions import get_subscriptions

#path = os.path.dirname(__file__) + "/mocks/"
msisdn = "96478"

def test():
    return [{'wallet': get_wallet(msisdn).dict()},
            {'subscriptions': [ one.dict() for one in get_subscriptions(msisdn)]},
            {'sim': get_sim_details(msisdn).dict()}
            ]
#@requests_mock.Mocker()
#def test(m):
#    m.get(settings.zend_api + '/esb/balance' , text=Path(path+'./my.json').read_text()) 
#    r1 = get_wallet(msisdn)
#    
#    return [ {'get_wallet' : r1} ]
