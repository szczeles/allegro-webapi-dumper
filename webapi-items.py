# coding: utf-8
from itemsqueue import ItemsQueue
from allegro import Allegro
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import json
import datetime
import time
import io
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

queue = ItemsQueue('queue.sq3')

def today_date():
  return datetime.datetime.now().strftime("%Y-%m-%d")

def dumpitems(items):
  with io.open("items.%s.txt" % today_date(), "a+", encoding='utf8') as itemsfile:
    for item in items:
      mark_status([item['itemInfo']['itId']], ItemsQueue.DONE)
      j = json.dumps(item, ensure_ascii=False, encoding='utf8')
      itemsfile.write(j + "\n")

def mark_status(ids, status):
  if ids != None:
    for id in ids:
      queue.markStatus(id, status)

allegro = Allegro()
allegro.load_credentials('.credentials')
concurrency = 5

while True:
  sample = queue.getWaiting(50000)
  print "Will download %d items" % len(sample)
  if len(sample) > 0:
    executor = ThreadPoolExecutor(max_workers=concurrency)
    futures = []
    for chunk in [sample[x:x+25] for x in range(0, len(sample), 25)]:
      futures.append(executor.submit(allegro.getItemsInfo, chunk))

    for idx, future in enumerate(futures):
      try:
        done, not_found, killed = future.result()
        mark_status(not_found, ItemsQueue.NOT_FOUND)
        mark_status(killed, ItemsQueue.KILLED)
        dumpitems(done)
        queue.commit()
        futures[idx] = None
      except:
        print("Chunk failed", sample[idx * 25:idx *25 + 25], sys.exc_info()[1])

      sys.stdout.write('.' if len(done) == 25 else '+')
      sys.stdout.flush()

    sys.stdout.write("\n")
    sys.stdout.flush()
    executor.shutdown()
  else:
    time.sleep(60)
