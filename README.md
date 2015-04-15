Power Grid Information System
=========================

## Installation

Install Postgresql and Postgis:

```
sudo apt-get install postgresql-9.3
sudo apt-get install postgresql-9.3-postgis-2.1
```

create database and enable postgis:

```
sudo -u postgres psql
> CREATE DATABASE gis;
> \connect gis
> CREATE EXTENSION postgis;
```

Download and install miniconda package, containing conda package manager and Anaconda distribution of Python. (Use Python version 3.4)

```
wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh 
```
follow the instructions of the installation process.

Create a virtual environment for the project:

```
conda create -n pgisenv anaconda python=3
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

Install nodejs, npm (Used by less asset compiler) and less:

```
sudo apt-get install nodejs
ln -s /usr/bin/nodejs /usr/bin/node
sudo apt-get install npm
sudo npm install -g less
```

## Running

With a builting server (not ok for production):

```
./run
```

Or with gunicorn:

```
gunicorn app:GisApp --bind localhost:3000
```

## Testing

```
nosetests tests
```
