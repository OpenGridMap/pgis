Power Grid Information System
=========================

## Installation

Download and install miniconda package, containing conda package manager and Anaconda's distribution of Python. (Use python version 3.4)

Create a virtual environment for the project:

``conda create -n gisenv anaconda python=3``

Activate virtual environment:

``source activate gisenv``

Install python dependencies:

``pip install -r requirements.txt``

## Running the app

With a builting server (not ok for production):

`./run`

Or with gunicorn:

`gunicorn app:GisApp --bind localhost:3000`

## Testing
