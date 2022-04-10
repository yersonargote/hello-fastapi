
TORTOISE_ORM = {
    "connections": {"default": "sqlite://hello-fast.db"},
    "apps": {
        "models": {
            "models": ["models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}

