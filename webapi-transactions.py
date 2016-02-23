#!/usr/bin/python3

from dumperqueue import DumperQueue
from allegro import Allegro
from concurrent.futures import ThreadPoolExecutor
import json
import datetime
import time
import io
import sys
import traceback


queue = DumperQueue('dumper.sq3')
allegro = Allegro()
allegro.load_credentials('.credentials')
concurrency = 10

def today_date():
	return datetime.datetime.now().strftime("%Y-%m-%d")

def dump_transactions(transactions):
	with io.open("transactions.%s.txt" % today_date(), "a+", encoding='utf8') as file:
		for transactions in transactions:
			file.write(json.dumps(transaction, ensure_ascii=False) + "\n")

def download_transactions(transactions):
	ids = [tr[1] for tr in transactions]
	items, not_found, killed = allegro.get_items_info(ids)
	if len(killed) > 0:
		print("Killed items:", killed)
	if len(not_found) > 0:
		print("Not found items:", not_found)
	items = {item['itemInfo']['itId']: item for item in items}
	transactions_with_items = []
	killed_info = []
	for transaction in transactions:
		if transaction[1] in items:
			tr_info = items[transaction[1]]
			tr_info['transaction'] = {
				'id': transaction[0],
				'date': transaction[2],
				'isBuyNow': transaction[2] == 1
			}
			transactions_with_items.append(tr_info)
		if transaction[1] in killed:
			killed_info.append(transaction[0])
	return transactions_with_items, killed_info

while True:
	sample = queue.get_transactions(10000)
	print("Will download %d transactions" % len(sample))
	if len(sample) > 0:
		executor = ThreadPoolExecutor(max_workers=concurrency)
		futures = []
		for chunk in [sample[x:x+25] for x in range(0, len(sample), 25)]:
			futures.append(executor.submit(download_transactions, chunk))
		
		for idx, future in enumerate(futures):
			try:
				result, killed_info = futures[idx].result()
				for transaction in result:
					queue.mark_downloaded(transaction['transaction']['id'])

				for id in killed_info:
					queue.mark_downloaded(id)

				dump_transactions(result)
				queue.commit()
				futures[idx] = None
			except:
				print("Chunk failed", list(map(lambda t: t[1], sample[idx * 25:idx *25 + 25])), sys.exc_info()[1])
				traceback.print_exc()

			sys.stdout.write('.' if result != None and len(result) == 25 else '+')
			sys.stdout.flush()

		sys.stdout.write("\n")
		sys.stdout.flush()
		executor.shutdown()
	else:
		time.sleep(60)
