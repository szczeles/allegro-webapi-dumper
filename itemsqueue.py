import sqlite3

class ItemsQueue:

    SCHEMA = '''
    CREATE TABLE IF NOT EXISTS itemsqueue
    (itemid INTEGER PRIMARY KEY, status INTENER)
    '''

    WAITING=0
    DONE=1
    NOT_FOUND=2
    KILLED=3

    def __init__(self, filename):
        self.conn = sqlite3.connect(filename, timeout=300)
	self.conn.execute("PRAGMA busy_timeout = 30000") 
	self.cur = self.conn.cursor()
	self.cur.execute(self.SCHEMA)
	
    def addNew(self, item):
        self.cur.execute('INSERT OR IGNORE INTO itemsqueue VALUES (?, ?)', (item, self.WAITING))

    def markStatus(self, item, status):
	self.cur.execute('UPDATE itemsqueue SET status=? WHERE itemid=?', (status, item))

    def getWaiting(self, limit):
        self.cur.execute('SELECT itemid FROM itemsqueue WHERE status=? LIMIT ?', (self.WAITING, limit))
	return [result[0] for result in self.cur.fetchall()]

    def commit(self):
        self.conn.commit()

    def getStats(self):
        self.cur.execute('SELECT count(*), status FROM itemsqueue GROUP BY status')
	return self.cur.fetchall()
