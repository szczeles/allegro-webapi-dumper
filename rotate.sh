#!/bin/sh

cd `dirname $0`
yesterday=`date +%Y-%m-%d -d '-1 day'`

bzip2 *$yesterday.txt && mv -b *.bz2 ~/hubic

export DBUS_SESSION_BUS_ADDRESS='unix:abstract=/tmp/dbus-NQAi5Q23SP,guid=8639f6d1b92eb867c4e5409656c0cbcd';

hubic backup update hubic
