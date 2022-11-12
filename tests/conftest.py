"Test configuration"

import sys

import praw
import praw.exceptions
import pytest
import yaml


@pytest.fixture(scope="session")
def conf() -> dict:
    """Load configuration"""
    try:
        with open("config.yaml", "rt", encoding="utf8") as file:
            config = yaml.safe_load(file)
            return config
    except OSError as e:
        print("Unable to load configuration", file=sys.stderr)
        raise e


@pytest.fixture(scope="session")
def reddit(conf) -> praw.Reddit:  # pylint: disable=redefined-outer-name
    """Retrieve a PRAW Reddit instance"""
    instance: praw.Reddit = praw.Reddit(
        client_id=conf.get("reddit").get("app_id"),
        client_secret=conf.get("reddit").get("app_secret"),
        username=conf.get("reddit").get("username"),
        password=conf.get("reddit").get("password"),
        user_agent="modnote-snoonote-importer by /u/Techman-",
        # Timeout in seconds
        # https://praw.readthedocs.io/en/stable/getting_started/ratelimits.html
        # Seconds * Minutes * Hours
        timeout=60 * 60 * 5,
    )
    if instance.read_only:
        raise praw.exceptions.ReadOnlyException
    return instance
