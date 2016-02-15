# coding: utf-8

import hashlib
import logging
from suds.client import Client, WebFault
from suds.sudsobject import asdict
import ConfigParser
 
class Allegro:
 
    def __init__(self, debug_mode=False):
        API_URL = 'https://webapi.allegro.pl/service.php?wsdl'
	self.client = Client(API_URL)
        self.service = self.client.service
        self.auth = None
        self.version_key = None
        if debug_mode:
            logging.basicConfig(level=logging.INFO)
            logging.getLogger('suds.client').setLevel(logging.DEBUG)

    def loadCredentials(self, filename):
        config = ConfigParser.RawConfigParser()
	config.read(filename)
	self.loginEnc(
	    config.get('allegro', 'api_key'), 
	    config.get('allegro', 'login'), 
	    config.get('allegro', 'password_enc'), 
	    config.getint('allegro', 'country_code')
	)
 
    def _get_version_by_country_code(self, country_code):
        systems = self.service.doQueryAllSysStatus(**{
            'countryId': country_code,
            'webapiKey':self.api_key
        })[0]
 
        for sys in systems:
            if sys['countryId'] == country_code:
                return sys['verKey']
 
    def loginEnc(self, api_key, login, password, country_code):
        try:
	    self.api_key = api_key
            self.version_key = self._get_version_by_country_code(country_code)
            self.auth = self.service.doLoginEnc(**{
                'userLogin': login,
                'userHashPassword': password,
                'countryCode': country_code,
                'webapiKey' : self.api_key,
                'localVersion' : self.version_key
            })
        except WebFault as ex:
            print ex

    def getSiteJournal(self, journalStart):
        items = self.service.doGetSiteJournal(**{
	    'sessionHandle': self.auth['sessionHandlePart'],
	    'startingPoint': journalStart,
	    'infoType': 1
	})['item']
	return [asdict(item) for item in items]

    def recursive_asdict(self, d):
        """Convert Suds object into serializable format."""
        out = {}
        for k, v in asdict(d).iteritems():
            if hasattr(v, '__keylist__'):
                out[k] = self.recursive_asdict(v)
            elif isinstance(v, list):
                out[k] = []
                for item in v:
                    if hasattr(item, '__keylist__'):
                        out[k].append(self.recursive_asdict(item))
                    else:
                        out[k].append(item)
            else:
                out[k] = v
        return out

    def getItemsInfo(self, items, getDesc=False, getImageUrl=True, getAttribs=True, getPostageOptions=True, getCompanyInfo=True):
        arr = self.client.factory.create('tns:ArrayOfLong')
	arr.item = items
        result = self.service.doGetItemsInfo(**{
	    'sessionHandle': self.auth['sessionHandlePart'],
	    'itemsIdArray': arr,
	    'getDesc' : int(getDesc),
	    'getImageUrl' : int(getImageUrl),
	    'getAttribs' : int(getAttribs),
	    'getPostageOptions' : int(getPostageOptions),
	    'getCompanyInfo' : int(getCompanyInfo),
	    'getProductInfo' : 0
	})
	not_found = result['arrayItemsNotFound']['item'] if 'item' in result['arrayItemsNotFound'] else None
	killed = result['arrayItemsAdminKilled']['item'] if 'item' in result['arrayItemsAdminKilled'] else None
	found = []
	if 'item' in result['arrayItemListInfo']:
	  for item in result['arrayItemListInfo']['item']:
	    found.append(self.recursive_asdict(item))
	return found, not_found, killed

    def getBidItem(self, itemid):
        raw_bids = self.service.doGetBidItem2(**{
	    'sessionHandle': self.auth['sessionHandlePart'],
	    'itemId': itemid
	})['item']
	bids = [data['bidsArray']['item'] for data in raw_bids]
	# TODO
	return bids#[asdict(item) for item in items]
