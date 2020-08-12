app_name = "Generic Persuasion Engine"

# DATABASE CONFIGURATIONS...

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        # Add "postgresql_psycopg2", "postgresql", "mysql", "sqlite3" or "oracle".
        "NAME": "goibibo_inventory",  # Or path to database file if using sqlite3.
        "USER": "gouser",  # Not used with sqlite3.
        "PASSWORD": "gi@G0u8eR",  # Not used with sqlite3.
        "HOST": "pp.mysql.goibibo.dev",  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",  # Set to empty string for default. Not used with sqlite3.
        "OPTIONS": {"autocommit": True},
        # "OPTIONS":{"init_command":"SET storage_engine=INNODB"},
    }
}

KAFKA_SERVER = {
    "PRODUCER": {
        "HOST": "localhost:9092",
        "TOPIC": "persuasion-test"
    },
    "CONSUMER": {
        "HOST": "localhost:9092",
        "TOPIC": "persuasion-test"
    }
}
