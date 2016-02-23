import sqlite3

class DumperQueue:
	TRANSACTIONS_SCHEMA = '''
	CREATE TABLE IF NOT EXISTS transactions (
		id INTEGER PRIMARY KEY,
		item INTEGER,
		change_date INTEGER,
		is_buynow BOOLEAN
	)
	'''

	BID_INFO_SCHEMA = '''
	CREATE TABLE IF NOT EXISTS bidinfo (
		itemid INTEGER PRIMARY KEY,
		last_action INTEGER
	)
	'''

	def __init__(self, filename):
		self.conn = sqlite3.connect(filename, timeout=300)
		self.conn.execute("PRAGMA busy_timeout = 30000") 
		self.cur = self.conn.cursor()
		self.cur.execute(self.TRANSACTIONS_SCHEMA)
		self.cur.execute(self.BID_INFO_SCHEMA)
	
	def add_transaction(self, transaction_id, item_id, change_date, is_buynow):
		self.cur.execute('INSERT OR IGNORE INTO transactions VALUES (?, ?, ?, ?)', (
			transaction_id,
			item_id,
			change_date,
			1 if is_buynow else 0
		))
		self.cur.execute('DELETE FROM bidinfo WHERE itemid=?', (item_id,))

	def mark_downloaded(self, transaction_id):
		self.cur.execute('DELETE FROM transactions WHERE id=?', (transaction_id,))

	def bid_occured(self, item_id, timestamp):
		self.cur.execute('INSERT OR REPLACE INTO bidinfo VALUES (?, ?)', (item_id, timestamp))

	def commit(self):
		self.conn.commit()

	def filter_auctions(self, ids):
		placeholder = '?'
		placeholders= ', '.join(placeholder for unused in ids)
		self.cur.execute('SELECT itemid FROM bidinfo WHERE itemid IN (%s)' % placeholders, ids) 
		return [item[0] for item in self.cur.fetchall()]

	def get_transactions(self, limit):
		self.cur.execute('SELECT * FROM transactions LIMIT ?', (limit,))
		return self.cur.fetchall()

	def get_stats(self):
		self.cur.execute('SELECT count(*) FROM transactions')
		transactions = self.cur.fetchall()[0][0]
		self.cur.execute('SELECT count(*) FROM bidinfo')
		bids = self.cur.fetchall()[0][0]
		return {'transactions': transactions, 'bids': bids}
