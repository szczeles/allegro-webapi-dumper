#!/usr/bin/python3 -u

from dumperqueue import DumperQueue
from allegro import Allegro
from multiprocessing.pool import Pool
import signal
import json
import datetime
import time
import io
import sys
import traceback


queue = DumperQueue('dumper.sq3')
allegro = Allegro()
allegro.load_credentials('.credentials')
allegro._perform_login()
concurrency = 3

def today_date():
	return datetime.datetime.now().strftime("%Y-%m-%d")

def dump_transactions(transactions):
	with io.open("transactions.%s.txt" % today_date(), "a+", encoding='utf8') as file:
		for transaction in transactions:
			if is_valid_transaction(transaction):
				transaction['itemInfo']['itDescription'] = None
				file.write(json.dumps(transaction, ensure_ascii=False) + "\n")

def is_valid_transaction(item):
	if item['transaction']['isBuyNow'] == False and item['itemInfo']['itBidCount'] == 0:
		print("All bids cancelled in", item['itemInfo']['itId'])
		return False

	if item['transaction']['isBuyNow'] == False and item['itemInfo']['itReservePrice'] == -1:
		print("Minimal price not reached in", item['itemInfo']['itId'])
		return False
	return True

def download_transactions(transactions):
	ids = [tr[1] for tr in transactions]
	items, not_found, killed = allegro.get_items_info(ids)
	items = {item['itemInfo']['itId']: item for item in items}
	transactions_with_items = []
	killed_info = []
	for transaction in transactions:
		if transaction[1] in items:
			tr_info = items[transaction[1]]
			tr_info['transaction'] = {
				'id': transaction[0],
				'date': transaction[2],
				'isBuyNow': transaction[3] == 1
			}
			transactions_with_items.append(tr_info)
		if transaction[1] in killed:
			killed_info.append(transaction[0])
	return transactions_with_items, killed_info

def download_catching_exceptions(chunk):
	try:
		result = download_transactions(chunk)
		sys.stdout.write('.' if result != None and len(result) == 25 else '+')
		sys.stdout.flush()
		return result
	except:
		print("Chunk failed", list(map(lambda t: t[1], sample[idx * 25:idx *25 + 25])), sys.exc_info()[1])
		traceback.print_exc()
		return [], []


pool = Pool(processes=concurrency)

def term(*args,**kwargs):
	pool.close()
	pool.terminate()
	pool.join()

signal.signal(signal.SIGTERM, term)
while True:
	sample = queue.get_transactions(10000)
	print("Will download %d transactions" % len(sample))
	if len(sample) < 25 * concurrency:
		time.sleep(60)
		continue

	chunks = [sample[x:x+25] for x in range(0, len(sample), 25)]
	start = time.time()
	results = pool.map(download_transactions, chunks)
	print("Data downloaded in %.2f sec/chunk, dump started" % ((time.time() - start) / len(chunks)))

	start = time.time()
	for result in results:
		for transaction in result[0]:
			queue.mark_downloaded(transaction['transaction']['id'])
		dump_transactions(result[0])
		for id in result[1]:
			queue.mark_downloaded(id)

	print("Data dumped %.2f sec/chunk" % ((time.time() - start) / len(chunks)))
	results = None
	queue.commit()

	sys.stdout.write("\n")
	sys.stdout.flush()
