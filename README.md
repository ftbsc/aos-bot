# AoS Discord Bot
Bot for controlling an [Ace of Spades](https://www.buildandshoot.com/) server ([piqueserver](https://github.com/piqueserver/piqueserver)) Docker instace through Discord, powered by [hikari](https://github.com/hikari-py/hikari). It's oddly specific, but that's what we used for.

Made by [Fraaz](https://github.com/realfraze) and [Tonio](https://github.com/tonio-cartonio) for [PoobAoS](https://aos.pooblic.org).

## Usage
### Configuration
All configuration is done by editing the [settings.toml](https://github.com/fantabos-co/aos-bot/blob/master/settings.toml).
### Commands
```
help              -> Prints this message.
ip                -> Returns the IP of the server.
check             -> Check whether your discord account is authorized to use the bot.
map add           -> Sends the file attachment (must be .vxl or .txt) to the maps folder.
map get <file>    -> Sends the requested map file. 
map remove <file> -> Deletes the provided filename from the config/maps folder.
map list          -> Lists all the files in the config/maps folder.
cfg               -> Replaces the config.toml file with a given attachment.
cfg get           -> Sends the current config file.
cfg <TOML expr>   -> Changes the given property in config/config.toml. Example: cfg name="Pooblic".
server restart    -> Restarts the server (needed for config changes).
server start      -> Starts the server.
server stop       -> Stops the server.
server kill       -> Kills the server.
server pause      -> Pauses the server.
server unpause    -> Unpauses the server.
server status     -> Returns the current status of the server.
```

## Notes
Do not give access to the bot to people you do not trust. Someone able to change configuration can potentially do very nasty things to your server. It's within Docker, so the machine itself SHOULD be safe, but better safe than sorry.
