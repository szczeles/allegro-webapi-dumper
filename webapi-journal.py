# coding: utf-8
from itemsqueue import ItemsQueue
from allegro import Allegro
import json
import datetime
import time
import glob
 

def today_date():
  return datetime.datetime.now().strftime("%Y-%m-%d")

def dumpitems(items):
  for item in items:
    if item['changeType'] == 'now':
      queue.addNew(item['itemId'])

  queue.commit()

  with open("journal.%s.txt" % today_date(), "a+") as journal:
    for item in items:
      journal.write(json.dumps(item) + "\n")

    print('Currently at %s, gathered events: %d' % (datetime.datetime.fromtimestamp(item['changeDate']).strftime('%Y-%m-%d %H:%M:%S'), len(items)))

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

queue = ItemsQueue('queue.sq3')

allegro = Allegro()
allegro.load_credentials('.credentials')

start = get_starting_point()
print("Starting from %d" % start)

while True:
  items = allegro.getSiteJournal(start)
  if len(items) > 0:
    dumpitems(items)
    start=items[-1]['rowId']
  if len(items) < 100:
    time.sleep(60)
