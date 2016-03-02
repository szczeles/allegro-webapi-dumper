#!/usr/bin/python3 -u

from dumperqueue import DumperQueue
from allegro import Allegro
import json
import datetime
import time
import glob
 
def today_date():
	return datetime.datetime.now().strftime("%Y-%m-%d")

def mark_actions(journal):
	for event in journal:
		if event['changeType'] == 'now':
			queue.add_transaction(event['rowId'], event['itemId'], event['changeDate'], True)
		elif event['changeType'] == 'bid':
			queue.bid_occured(event['itemId'], event['changeDate'])

	queue.commit()

def mark_auctions_wins(journal):
	ends = []
	for event in journal:
		if event['changeType'] == 'end':
			ends.append(event['itemId'])

	only_auctions = queue.filter_auctions(ends)
	for event in journal:
		if event['changeType'] == 'end' and event['itemId'] in (only_auctions):
			queue.add_transaction(event['rowId'], event['itemId'], event['changeDate'], False)

	queue.commit()

def dump_journal(journal):
	with open("journal.%s.txt" % today_date(), "a+") as journaldump:
		for event in journal:
			journaldump.write(json.dumps(event) + "\n")

	print('Currently at %s, gathered events: %d' % (datetime.datetime.fromtimestamp(event['changeDate']).strftime('%Y-%m-%d %H:%M:%S'), len(journal)))

queue = DumperQueue('dumper.sq3')

allegro = Allegro()
allegro.load_credentials('.credentials')
start = queue.get_status()['last_journal_rowid']
print("Starting from %d" % start)

while True:
	journal = allegro.get_site_journal(start)
	if len(journal) > 0:
		mark_actions(journal)
		mark_auctions_wins(journal)
		dump_journal(journal)
		queue.set_status(last_journal_rowid=start, last_journal_timestamp=journal[-1]['changeDate'])
		start=journal[-1]['rowId']
	if len(journal) < 100:
		time.sleep(60)
