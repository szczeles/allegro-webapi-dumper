#!/bin/bash

cd `dirname $0`
yesterday=`date +%Y-%m-%d -d '-1 day'`

bzip2 *$yesterday.txt && mv -b *.bz2 ~/hubic

dbus-launch --sh-syntax > /tmp/dbus
source /tmp/dbus
hubic backup update hubic
