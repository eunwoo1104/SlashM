# SlashM
Python Discord music bot using slash command and discodo.  
Note: This only supports Korean.

## How to run?
1. Clone this repo.
2. Create `bot_settings.json`, and write this to that file.
    ```json
    {
        "stable_token": "your-bot-token-here",
        "debug": false
    }
    ```
3. Install all dependencies.
4. Open `cogs/music.py`, then replace ID in the `guild_ids` list to your testing guild ID.
You can just set `guild_ids` to empty list to make as global comand.
5. Run the bot.
