# AoS Discord Bot
Bot for controlling an [Ace of Spades](https://www.buildandshoot.com/) server ([piqueserver](https://github.com/piqueserver/piqueserver)) through Discord, powered by [hikari](https://github.com/hikari-py/hikari).

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

