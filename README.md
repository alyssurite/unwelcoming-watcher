# The Kick Bot

Telegram group bot with no welcoming messages that kicks you.

## How to launch the bot

Create and configure `.env` file. See `example.env` for details.

Update Python dependencies:

```shell
poetry update
```

Then run database migrations:

```shell
alembic upgrade head
```

Then start the bot:

```shell
poetry run python bot
```
