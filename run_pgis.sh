#!/bin/bash

sudo service nginx restart

source activate pgisenv

kill -9 `ps aux |grep gunicorn |grep app:GisApp | awk '{ print $2 }'`

gunicorn app:GisApp -w 4


