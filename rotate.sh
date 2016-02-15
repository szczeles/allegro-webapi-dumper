#!/bin/sh

cd `dirname $0`
yesterday=`date +%Y-%m-%d -d '-1 day'`

bzip2 *$yesterday.txt && mv -b *.bz2 ~/hubic
