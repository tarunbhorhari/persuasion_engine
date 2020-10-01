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
    "host": "host.docker.internal:9092",
    "topic": {
        "persuasion": "persuasion-test",
        "watson": "persuasion-test1",
        "inflow": "persuasion-test2"

    },
    "group": {
        "persuasion": "persuasion"
    }
}

DYNAMIC_DATA_ELASTIC_SEARCH = {
    "host": "vpc-ingoibibo-analytics-es-4jgoflixwmiwoz7waoejlz4cay.ap-south-1.es.amazonaws.com",
    "protocol": "https",
    "port": 443
}

STATIC_DATA_ELASTIC_SEARCH = {
    "host": "vpc-ingoibibo-static-es-rmp73cf7aa4mjpjzaq6qdj7t2a.ap-south-1.es.amazonaws.com",
    "protocol": "https",
    "port": 443
}

PERSUASION_ES_INDEX = "persuasions_test"
INVENTORY_DEPTH_ES_INDEX = "qsInventoryDepth"

PERSUASION_STATUS = [
    "NEW", "UPDATED", "EXPIRED", "RESOLVED"
]

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TEAMS_NOTIFICATION_URL = "https://outlook.office.com/webhook/eed8c571-d7e7-4efa-934b-7618a7d2845a@268b4680-2b9f-4060-8038-d5f6b23352bf/IncomingWebhook/a74dee06c7744153b4f15d2a659a762a/a013704c-99ce-4d74-9d85-bfbc0cc8acc2"
MAX_WORKERS = 20

CONFIG_KEEPER_HOST_PROTOCOL = "https"
CONFIG_KEEPER_HOST = "configkeeperpp.goibibo.com"
CONFIG_KEEPER_SERVICE_NAME = "persuasion_engine"
CONFIG_KEEPER_CATEGORY = "templates"
CONFIG_KEEPER_URL = CONFIG_KEEPER_HOST_PROTOCOL + "://" + CONFIG_KEEPER_HOST + "/api/v1/fetch-config/?service="

TEMPLATE_CHOICES = {
    "inventory": ["sold_out", "fast_filling"],
    "quality_score": ["inventory_depth", "content_score"]
}

TEMPLATE_CHANNEL_NAME = "persuasion_engine_templates"
REDIS_SERVER = {
    "host": "host.docker.internal",
    "port": 6379,
    "db": 12
}

FLASK = {
    "host": "0.0.0.0",
    "port": 5000
}
