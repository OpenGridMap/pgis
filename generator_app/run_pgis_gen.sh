#!/bin/bash

source activate generator

kill -9 `ps aux |grep gunicorn |grep app:GisGeneratorApp | awk '{ print $2 }'`

gunicorn -b 127.0.0.1:9000 app:GisGeneratorApp

