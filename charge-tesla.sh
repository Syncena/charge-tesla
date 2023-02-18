#!/bin/sh

/bin/echo "" >> /tmp/charge-tesla.log
/bin/echo "`/bin/date`" >> /tmp/charge-tesla.log
/usr/local/sbin/charge-tesla.py $* >> /tmp/charge-tesla.log 2>&1
