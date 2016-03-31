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
  * OS X
  
    Easiest way is to download and install the [postregapp](http://postgresapp.com/). Download [PostgreSQL 9.3 with PostGIS 2.1](https://github.com/PostgresApp/PostgresApp/releases/download/9.3.10.0/Postgres-9.3.10.0.zip) and copy the app to your `/Applications` folder.
  

2. Create database and enable postgis:
  
  ```
  sudo -u postgres psql
  > CREATE DATABASE gis;
  > \connect gis
  > CREATE EXTENSION postgis;
  ```
  <b>Note:</b> Mac users who have downloaded the postgres.app might have to mind the username passed with `-u` in the command above. The user `postgres`(which is default in many postgres installations) might not be present. The postgres.app will create an user with the same username as a your OS X's username as default user. So use your OS X's username instead of `postgres`

3. Miniconda 
  Download and install miniconda package, containing conda package manager and Anaconda distribution of Python. (Use Python version 3.4)
 * Ubuntu
    
    ````
    wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
    chmod +x Miniconda3-latest-Linux-x86_64.sh
    ./Miniconda3-latest-Linux-x86_64.sh 
    ````
    
    follow the instructions of the installation process.

 * OS X
   
    Download and run the [Anaconda3-2.3.0-MacOSX-x86_64.pkg](https://repo.continuum.io/archive/Anaconda3-2.3.0-MacOSX-x86_64.pkg) installer from https://repo.continuum.io/archive/index.html which contains the correct python version(which is 3.4) we use for the project.

4. Create a virtual environment for the project:

   ````
   conda create -n pgisenv anaconda python=3.4.1
   ````

5. Clone the repository:

   ````
   git clone git@github.com:OpenGridMap/pgis.git
   cd pgis/
   ````

6. Activate virtual environment:

   ````
   source activate pgisenv
   ````

7. Install Python dependencies:

   ````
   pip install -r requirements.txt
   ````

8. Run migrations:

   ````
   ./manage db upgrade
   ````

9. Install nodejs, npm (Used by less asset compiler) and less:

   ````
   sudo apt-get install nodejs
   ln -s /usr/bin/nodejs /usr/bin/node
   sudo apt-get install npm
   sudo npm install -g less
   ````

8. Install kmeans clustering extension for Postgis:

   ````
   wget http://api.pgxn.org/dist/kmeans/1.1.0/kmeans-1.1.0.zip
   unzip kmeans-1.1.0.zip
   cd kmeans-1.1.0/
   export USE_PGXS=1  # in bash
   
   make
   make install
   psql -f /usr/share/postgresql/9.3/extension/kmeans.sql -U postgres -d gis
   ````

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

## Troubleshooting Installation - On OS X

* During `pip install -r requirements.txt`
   * `Library not loaded: libcrypto.1.0.0.dylib` while installing cryptography
        * in the active bash session, do `export DYLD_LIBRARY_PATH=$HOME/anaconda/lib` and re-run the command in then same bash session.
        * If you use a different bash session, the environmental variable will be lost. If you want this to be present in any future bash session, add the `export` line to your `.bashrc` or `.bash_profile` file.
   * `Error: could not invoke ['llvm-config', '--version']`
     * you need to install `llvmpy` on your conda env. According to the requirement.txt file, you need the version 0.12.7. You can install it with `conda install -c https://conda.anaconda.org/sklam llvmpy=0.12.7`.
     * From the command, you install `llvmpy` from sklam's repo instead of the usual anaconda's repo. You could also install from anaconda directly by `conda install llvmpy=0.12.7`. I installed sklam`s version because the other failed.
   * `Error: pg_config executable not found.`
     * Check the `postgresql` installation on your host computer. Find the `pg_config` executable path and append it to your `PATH` environmental variable.
     * If you have downlaoded and use `postgres.app` on your mac as in the installation instructions section, locate the `pg_config` executable in `/Applications/Postgres.app/Contents/Versions/<your version>/bin` and update your PATH environmental variable.
   * `ValueError: unknown locale: UTF-8`
     * Follow the instructions [http://conda.pydata.org/docs/troubleshooting.html#unknown-locale](http://conda.pydata.org/docs/troubleshooting.html#unknown-locale)
   * `ld: library not found for -lhdf5`
     * you need to set an environment variable for this too. Do `export HDF5_DIR=$HOME/anaconda/lib` in the current bash session and re-run the command in then same bash session.
     * If you use a different bash session, the environmental variable will be lost. If you want this to be present in any future bash session, add the `export` line to your `.bashrc` or `.bash_profile` file.
   *  `error: no member named 'f_tstate' in 'struct _frame'`
     *  Check which package was being tried to be installed while this error happened, it might be Cython. check the version for that package from `requirement.txt` file and do `conda install cython=0.211`. Change the package name and version based on your need.
   * `Found existing installation: Sphinx 1.3.1` or `Cannot remove entries from nonexistent file /Users/Munna/anaconda/lib/python3.4/site-packages/easy-install.pth`
     * This happens when there is a Sphinx installation already, find the version that is needed from the required from requirements.txt file and install that using `conda install sphinx=<version>`
