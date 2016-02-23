# coding: utf-8

import hashlib
import logging
import configparser
import pysimplesoap
import ssl
 
class Allegro:
	def __init__(self, debug_mode=False):
		API_URL = 'https://webapi.allegro.pl/service.php?wsdl'
		logging.basicConfig() # TODO?
		self.client = pysimplesoap.client.SoapClient(wsdl=API_URL, trace=debug_mode, strict=False)
		self.auth = ''

	def load_credentials(self, filename):
		config = configparser.RawConfigParser()
		config.read(filename)
		self.credentials = {
			'api_key': config.get('allegro', 'api_key'), 
			'login': config.get('allegro', 'login'), 
			'password_enc': config.get('allegro', 'password_enc'), 
			'country_code': config.getint('allegro', 'country_code')
		}
 
	def _get_version_by_country_code(self):
		systems = self.client.doQueryAllSysStatus(
			countryId=self.credentials['country_code'],
			webapiKey=self.credentials['api_key']
		)

		for sys in systems['sysCountryStatus']['item']:
			if sys['countryId'] == self.credentials['country_code']:
				return sys['verKey']
 
	def _perform_login(self):
		self.version_key = self._get_version_by_country_code()
		self.auth = self.client.doLoginEnc(**{
			'userLogin': self.credentials['login'],
			'userHashPassword': self.credentials['password_enc'],
			'countryCode': self.credentials['country_code'],
			'webapiKey' : self.credentials['api_key'],
			'localVersion' : self.version_key
		})['sessionHandlePart']

	def get_site_journal(self, journalStart):
		response = self._call_api('doGetSiteJournal', {
			'startingPoint': journalStart,
			'infoType': 1
		})['siteJournalArray']
		return response['item'] if response else []

	def _call_api(self, method_name, params):
		f = getattr(self.client, method_name)
		params['sessionHandle'] = self.auth
		try:
			return f(**params)
		except pysimplesoap.client.SoapFault as exception:
			if exception.faultcode in ['ERR_NO_SESSION', 'ERR_SESSION_EXPIRED']:
				self._perform_login()
				return self._call_api(method_name, params)
			raise

	def _repair_item(self, item):
		for key in ('itemImages', 'itemPostageOptions', 'itemCats', 'itemAttribs'):
			item[key] = item[key]['item'] if item[key] != None else []
		attribs = []
		for attrib in item['itemAttribs']:
			attribs.append({'attribName': attrib['attribName'], 'attribValues': list(map(lambda a: a['item'], filter(lambda a: 'item' in a, attrib['attribValues'])))}) 
		item['itemAttribs'] = attribs
		item.pop('itemProductInfo', None)
		return item

	def get_items_info(self, items, getDesc=False, getImageUrl=True, getAttribs=True, getPostageOptions=True, getCompanyInfo=True):
		result = self._call_api('doGetItemsInfo', {
			'itemsIdArray': [{'item': item} for item in items],
			'getDesc' : int(getDesc),
			'getImageUrl' : int(getImageUrl),
			'getAttribs' : int(getAttribs),
			'getPostageOptions' : int(getPostageOptions),
			'getCompanyInfo' : int(getCompanyInfo),
		})
		not_found = [item['item'] for item in result['arrayItemsNotFound']] if 'arrayItemsNotFound' not in result['arrayItemsNotFound'][0] else []
		killed = [item['item'] for item in result['arrayItemsAdminKilled']] if 'arrayItemsAdminKilled' not in result['arrayItemsAdminKilled'][0] else []
		found = list(map(self._repair_item, result['arrayItemListInfo']['item'])) if result['arrayItemListInfo'] != None and 'item' in result['arrayItemListInfo'] else []
		return found, not_found, killed
'''
    def getBidItem(self, itemid):
        #raw_bids = self.service.doGetBidItem2(**{
	#    'sessionHandle': self.auth['sessionHandlePart'],
	#    'itemId': itemid
	#})['item']
	#bids = [data['bidsArray']['item'] for data in raw_bids]
	# TODO
	#return bids#[asdict(item) for item in items]
	pass
'''
