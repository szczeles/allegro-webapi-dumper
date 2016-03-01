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
			print("Added now transaction:", event['rowId'])
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
			print("Added bid transaction:", event['rowId'])
			queue.add_transaction(event['rowId'], event['itemId'], event['changeDate'], False)

	queue.commit()

def dump_journal(journal):
	with open("journal.%s.txt" % today_date(), "a+") as journaldump:
		for event in journal:
			journaldump.write(json.dumps(event) + "\n")

	print('Currently at %s, gathered events: %d' % (datetime.datetime.fromtimestamp(event['changeDate']).strftime('%Y-%m-%d %H:%M:%S'), len(journal)))

def get_starting_point():
	start = 0
	for journal_file in glob.glob('./journal.*.txt'):
		with open(journal_file, 'rb') as fh:
			fh.seek(-1024, 2)
			lastline = fh.readlines()[-1].decode()
			lastid = int(json.loads(lastline)['rowId'])
			if lastid > start:
				start = lastid
	return start

queue = DumperQueue('dumper.sq3')

allegro = Allegro()
allegro.load_credentials('.credentials')

start = get_starting_point()
print("Starting from %d" % start)

while True:
	journal = allegro.get_site_journal(start)
	if len(journal) > 0:
		mark_actions(journal)
		mark_auctions_wins(journal)
		dump_journal(journal)
		start=journal[-1]['rowId']
	if len(journal) < 100:
		time.sleep(60)
