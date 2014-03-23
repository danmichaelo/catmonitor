#!/bin/sh

cd /data/project/catmonitor
. ENV/bin/activate
python catmonitor.py --silent --config config.no.yml

