# Import SnooNotes into Reddit Mod Notes
## Introduction
This is a small utility to help Reddit communities import their [SnooNote](https://snoonotes.com/) [[archive](https://web.archive.org/web/20220801175349/https://snoonotes.com/#!/)] backups into Reddit's [new Mod Notes feature](https://www.reddit.com/r/modnews/comments/t8vafc/announcing_mod_notes/). Unlike [Toolbox User Notes](https://www.reddit.com/r/toolbox/wiki/docs/usernotes/), which can be imported by contacting Reddit, SnooNotes is a 3rd-party service and thus the data from it is not already stored within Reddit.

This utility:
1. Reads your SnooNote backup/export file
2. Parses notes and note types
3. Maps SnooNote note types into their closest Mod Note counterpart
    * If a mapping is not available, you will receive an error and be asked to file an issue so that it may be added for everyone.
4. Converts SnooNotes into one or more Mod Notes
    * Mod Notes has a length limit, so longer notes will be split into multiple Mod Notes gracefully.


Converted notes will appear in the following format:
```
[ISO date string] [/u/moderator_name]
text
```

Example:
```
[2022-09-20T23:58:10+00:00] [/u/Techman-]
Test message #1
```
this is due to not being able to specify existing author information and timestamp. All converted notes will have time and author information prepended.

## Building
This project uses [Python Poetry](https://python-poetry.org/). It can be locally installed and run by:

1. Downloading the project (or using git clone)
2. Running `poetry install` within the project root (where you see .toml files, etc.)

This will install all necessary dependencies and install the package within the virtual environment.

## Running
Ensure you are running inside the virtual environment by typing `poetry shell`. Run the project by typing `python -m modnote_snoonote_importer <args>`

There are two options for running: using command line arguments, or specifying a configuration file. If both are supplied, the command line arguments are used.

### Using command line arguments

Type `python -m modnote_snoonote_importer --help` to view help information and required arguments.

Example:
`python -m modnote_snoonote-importer --app_id 'app id' --app_secret 'keep this safe' --username 'AVeryNiceBot' --password 'hunter2' <export file>`

### Using a configuration file
Copy `config.example.yaml` to `config.yaml` and fill in the empty fields. Every field is explained with a comment immediately above it. Then, run using `python -m modnote_snoonote_importer --config config.yaml <export file>`

Before running, you will need a user account (preferably a bot account) with the **Manage Users** permission on the subreddit you are importing into. You will also need to create a [custom application](https://old.reddit.com/prefs/apps/) on Old Reddit to receive your own `app_id` and `app_secret`. You will also need the account's `username` and `password` handy.

## Bugs/Issues
Please file a GitHub issue if you are having issues with using the utility. Please include as much information as possible, but **do not post your authentication credentials publicly**.

## Testing
This project uses `pytest` for tests. You can run them inside the virtual environment by running `pytest` or `python -m pytest`. These tests do make use of the Reddit API.

**Note**: A configuration file ***must*** be used for tests. The tests will look for a `config.yaml` file before proceeding.
