
TORTOISE_ORM = {
    "connections": {"default": "sqlite://hello-fast.db"},
    "apps": {
        "models": {
            "models": ["app.models"],
            "default_connection": "default",
        },
    },
    "use_tz": True,
}

