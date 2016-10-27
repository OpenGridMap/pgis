import os

basedir = os.path.abspath(os.path.dirname(__file__))

import yaml


def read_yaml_configuration_for(config_type):
    file_name = os.path.dirname(__file__) + "/{0}.yml".format(config_type)
    if os.path.isfile(file_name):
        with open(file_name, 'r') as f:
            config_from_file = yaml.load(f)
    else:
        raise Exception("{0} configuration not found. " \
                        "Copy +{0}.yml.example+ as +{0}.yml+ " \
                        "and update the configuration to match " \
                        "your system's.".format(config_type))
    return config_from_file


db_config = read_yaml_configuration_for('database')
app_config = read_yaml_configuration_for('application')


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


database_uri = "postgresql://{0}:{1}@{2}:{3}/{4}"


class Development(Config):
    DEBUG = True
    OSMAPI_CONFIG = app_config['development']['osmapi']
    SQLALCHEMY_DATABASE_URI = database_uri.format(db_config['development']['user'],
                                                  db_config['development']['password'],
                                                  db_config['development']['host'],
                                                  db_config['development']['port'],
                                                  db_config['development']['database'])


class Production(Config):
    OSMAPI_CONFIG = app_config['production']['osmapi']
    SQLALCHEMY_DATABASE_URI = database_uri.format(db_config['production']['user'],
                                                  db_config['production']['password'],
                                                  db_config['production']['host'],
                                                  db_config['production']['port'],
                                                  db_config['production']['database'])


class Test(Config):
    DEBUG = True
    OSMAPI_CONFIG = app_config['test']['osmapi']
    SQLALCHEMY_DATABASE_URI = database_uri.format(db_config['test']['user'],
                                                  db_config['test']['password'],
                                                  db_config['test']['host'],
                                                  db_config['test']['port'],
                                                  db_config['test']['database'])
