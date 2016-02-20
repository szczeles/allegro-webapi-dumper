# allegro-webapi-dumper
Tool that users allegro.pl webapi to download events journal and items info
Written in Python 3.4, requires pysimplesoap installed form github:

    pip3 install git+git://github.com/pysimplesoap/pysimplesoap.git

### webapi-journal

`webapi-journal.py` script downloads journal using method [doGetSiteJournal](http://allegro.pl/webapi/documentation.php/show/id,65)
and for every started or bought by clicking "buy-now" event adds item download request to sqlite-based queue. All journal events
are dumped to `journal.txt` files, partitioned by date.

### webapi-items

`webapi-items.py` script read items queue and retrieves item detail using method [doGetItemsInfo](http://allegro.pl/webapi/documentation.php/show/id,52). 
Items details are dumped to `items.txt` files, partitioned by date.
