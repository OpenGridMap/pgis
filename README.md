[![Stories in Ready](https://badge.waffle.io/OpenGridMap/pgis.png?label=ready&title=Ready)](https://waffle.io/OpenGridMap/pgis)
Power Grid Information System
=========================

[![Join the chat at https://gitter.im/OpenGridMap/pgis](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/OpenGridMap/pgis?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

## Installation

1. Install PostgreSQL and PostGIS:

  * Ubuntu:
  
    ```
    sudo apt-get install postgresql-9.3
    sudo apt-get install postgresql-9.3-postgis-2.1
    sudo apt-get install postgresql-server-dev-9.3
    ```
  * Mac
  
    Easiest way is to download and install the [postregapp](http://postgresapp.com/). Download [PostgreSQL 9.3 with PostGIS 2.1](https://github.com/PostgresApp/PostgresApp/releases/download/9.3.10.0/Postgres-9.3.10.0.zip) and copy the app to your `/Applications` folder.
  

2. Create database and enable postgis:
  
  ```
  sudo -u postgres psql
  > CREATE DATABASE gis;
  > \connect gis
  > CREATE EXTENSION postgis;
  ```
  <b>Note:</b> Mac users who have downloaded the postgres.app might have to mind the username passed with `-u` in the command above. The user `postgres`(which is default in many postgres installations) might not be present. The postgres.app will create an user with the same username as a your OS X's username as default user. So use your OS X's username instead of `postgres`

Download and install miniconda package, containing conda package manager and Anaconda distribution of Python. (Use Python version 3.4)

```
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh 
```
follow the instructions of the installation process.

Create a virtual environment for the project:

```
conda create -n pgisenv anaconda python=3.4.1
```

Clone the repository:

```
git clone git@github.com:OpenGridMap/pgis.git
cd pgis/
```

Activate virtual environment:

```
source activate pgisenv
```

Install Python dependencies:

```
pip install -r requirements.txt
```

Run migrations:

```
./manage db upgrade
```

Install nodejs, npm (Used by less asset compiler) and less:

```
sudo apt-get install nodejs
ln -s /usr/bin/nodejs /usr/bin/node
sudo apt-get install npm
sudo npm install -g less
```

Install kmeans clustering extension for Postgis:

```
wget http://api.pgxn.org/dist/kmeans/1.1.0/kmeans-1.1.0.zip
unzip kmeans-1.1.0.zip
cd kmeans-1.1.0/
export USE_PGXS=1  # in bash

make
make install
psql -f /usr/share/postgresql/9.3/extension/kmeans.sql -U postgres -d gis
```

## Running

With a built-in server (not ok for production):

```
./manage runserver
```

for production:

```
gunicorn app:GisApp --bind localhost:3000
```

## Testing

```
nosetests tests
```
