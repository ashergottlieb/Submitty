#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
from pathlib import Path

# Much is borrowed from partial_reset.py
# I cannot simply import due to way relative imports work in python, would make script more challenging to execute
CURRENT_PATH = Path(__file__).resolve().parent
SETUP_DATA_PATH = Path(CURRENT_PATH, "..", "data").resolve()
SUBMITTY_REPOSITORY = Path("/usr/local/submitty/GIT_CHECKOUT/Submitty")
SUBMITTY_INSTALL_DIR = Path("/usr/local/submitty")
SUBMITTY_DATA_DIR = Path("/var/local/submitty")

def cmd_exists(cmd):
    """
    Given a command name, checks to see if it exists on the system, return True or False
    """
    return shutil.which(cmd) is not None


def main():
    if not cmd_exists('psql'):
        raise SystemExit('Postgresql must be installed for this script to run!')

    with Path(SUBMITTY_INSTALL_DIR, 'config', 'database.json').open() as submitty_config:
        submitty_config_json = json.load(submitty_config)
        os.environ['PGPASSWORD'] = submitty_config_json["database_password"]
        db_user = submitty_config_json["database_user"]

    def postgres_cmd(db: str, cmd: str):
        subprocess.check_call(
            ['psql', '-d', db, '-U', db_user, '-c', cmd]
        )

    # please don't make this anything that I have to sanitize :)
    POSTGRES_DB_NAME = 'postgres'
    METRICS_DB_NAME = 'submitty_metrics'
    # note, postgres complains if you combine the two commands in one block.
    postgres_cmd(POSTGRES_DB_NAME, f'DROP DATABASE IF EXISTS {METRICS_DB_NAME};')
    postgres_cmd(POSTGRES_DB_NAME, f'CREATE DATABASE {METRICS_DB_NAME};')

    # TODO: move schema out of here!
    # TODO: extract event_type out into another table, and use a foreign key to reference it.
    schema = '''
    BEGIN;
    CREATE TABLE public.events (
        event_id SERIAL PRIMARY KEY,
        event_type character varying NOT NULL,
        timestamp timestamp NOT NULL,
        controller character varying,
        method character varying,
        trace jsonb NOT NULL,
        data jsonb NOT NULL
    );
    COMMIT;
    '''
    postgres_cmd(METRICS_DB_NAME, schema);

if __name__ == '__main__':
    main()

