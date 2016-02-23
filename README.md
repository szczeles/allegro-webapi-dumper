# allegro-webapi-dumper
Tool that users allegro.pl webapi to download events journal and items info
Written in Python 3.4, requires pysimplesoap installed form github:

    pip3 install git+git://github.com/pysimplesoap/pysimplesoap.git

### webapi-journal

`webapi-journal.py` script downloads journal using method [doGetSiteJournal](http://allegro.pl/webapi/documentation.php/show/id,65) and:

 * for every `buy-now` (`now`) event adds item details download request to queue
 * for every `bid` event creates `bidinfo` entry
 * for every `end` event checks if item was previosly bidded and adds item download request to the queue

Additionally all evens are dumped to `journal.txt` files, partitioned by date. 

### webapi-transactions

`webapi-transactions.py` script read items queue and retrieves item detail using method [doGetItemsInfo](http://allegro.pl/webapi/documentation.php/show/id,52). 
Items details with transaction info are dumped to `transactions.DATE.txt` files, partitioned by date.
