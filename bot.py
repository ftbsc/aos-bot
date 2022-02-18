import re
import os
import toml 
import docker
import logging

from pathlib import Path
from typing import Callable
from signal import SIGINT

from hikari import GatewayBot
from hikari.events import DMMessageCreateEvent

bot = GatewayBot(token="discord_bot_token")

OPERATOR = [] #Discord user IDs go here
OWNER = [] #and here

CONFIG_PATH = Path("Path to piqueserver/piqueserver/config").resolve()
DOCKER_NAME = "name of the docker container running piqueserver (you must have created it already)"
SERVER_IP = "IP of the server"

DELIMITER_FINDER = re.compile(r"([\"'])(.*?)(?<!\\)\1|(\S+)")
DELIMITER_REMOVER = re.compile(r"\\([\"'])")

HELP_TEXT = """
**COMMAND LIST**
```
help -> Prints this message.
ip -> Returns the IP of the server.
check -> Check whether your discord account is authorized to use the bot.
map add -> Sends the file attachment (must be .vxl or .txt) to the maps folder.
map get <filename> -> Sends the requested map file. 
map remove <filename> -> Deletes the provided filename from the config/maps folder.
map list -> Lists all the files in the config/maps folder.
cfg -> Replaces the config.toml file with a given attachment.
cfg get -> Sends the current config file.
cfg <TOML expression> -> Changes the given property in config/config.toml. Example: cfg name="Pooblic".
server restart -> Restarts the server (needed for config changes).
server start -> Starts the server.
server stop -> Stops the server.
server kill -> Kills the server.
server pause -> Pauses the server.
server unpause -> Unpauses the server.
server status -> Returns the current status of the server.
```
"""

def command(cmd:str, public:bool=False, sudo:bool=False) -> Callable:
	def decorator(fun: Callable) -> Callable:

		@bot.listen(DMMessageCreateEvent)
		async def wrapper(event: DMMessageCreateEvent) -> None:
			if event.is_bot or not event.content:
				return

			if not re.match(rf"{cmd}( |$)", event.content):
				return

			if not (
				public or
				(not sudo and (event.author_id in OPERATOR or event.author_id in OWNER)) or
				(sudo and event.author_id in OWNER)
			): 
				return

			logging.info(
				"[%s#%s] running '%s'",
				event.message.author.username,
				event.message.author.discriminator,
				event.message.content 
			)

			match_list = [
				DELIMITER_REMOVER.sub(r"\1", m.group(2) or m.group(3) or "")
				for m in DELIMITER_FINDER.finditer(event.content)
			]

			await fun(event, *match_list)
		return fun
	return decorator

@command("help", public=True)
async def help_cmd(event:DMMessageCreateEvent, *args) -> None:
	await event.message.respond(HELP_TEXT)

@command("ip", public=True)
async def url_cmd(event:DMMessageCreateEvent, *args) -> None:
	await event.message.respond(f"The server IP is `{SERVER_IP}`.")

@command("check", public=True)
async def check_cmd(event:DMMessageCreateEvent, *args) -> None:
	if event.author_id in OWNER:
		await event.message.respond("Damn you're OG")
	elif event.author_id in OPERATOR:
		await event.message.respond("Yep, you are authorized!")
	else:
		await event.message.respond("Shoo, you aren't allowed to use this.")

@command("map")
async def map_cmd(event:DMMessageCreateEvent, *args) -> None:
	if args[1] == "add":
		if event.message.attachments and len(event.message.attachments) > 0:
			for att in event.message.attachments:
				if att.extension not in ["txt", "vxl"]:
					await event.message.respond(f"`{att.filename}` is not a valid map file!")
				else:
					dest_path = (CONFIG_PATH / 'maps' / att.filename).resolve()
					try:
						dest_path.relative_to(CONFIG_PATH / 'maps')
					except ValueError:
						await event.message.respond("Your filename tried to mess with us. Uncool.")
						return
					async with att.stream() as stream:
						data = await stream.read()
						with open(dest_path, "wb") as f:
							f.write(data)
						await event.message.respond(f"Uploaded to `config/maps/{att.filename}`.")
		else:
			await event.message.respond("You need to attach a map file!")
	elif args[1] == "get":
		if len(args) < 3:
			await event.message.respond("Please provide a filename to download.")
			return
		dest_path = CONFIG_PATH / 'maps' /str.join(' ', args[2:])
		try:
			dest_path.relative_to(CONFIG_PATH / 'maps')
		except ValueError:
			await event.message.respond("Your filename tried to mess with us. Uncool.")
			return
		async with bot.rest.trigger_typing(event.channel_id):
			await event.message.respond(f"{dest_path.relative_to(CONFIG_PATH)}", attachment = dest_path)
	elif args[1] == "remove":
		if len(args) < 3:
			await event.message.respond("Please provide a filename to delete.")
			return
		dest_path = CONFIG_PATH / 'maps' / str.join(' ', args[2:])
		try:
			dest_path.relative_to(CONFIG_PATH / 'maps')
		except ValueError:
			await event.message.respond("Your filename tried to mess with us. Uncool.")
			return
		try:
			os.remove(dest_path)
			await event.message.respond(f"Removed `config/{dest_path.relative_to(CONFIG_PATH)}`.")
		except OSError:
			logging.exception("Exception while removing file") 
			await event.message.respond(f"`{dest_path}` is not a valid file.")
	elif args[1] == "list":
		maps = os.listdir(CONFIG_PATH / 'maps')
		reply = "```\nconfig/maps/"
		for m in maps:
			if m == "__pycache__":
				continue
			reply += f"\n|- {m}"
		reply += "```"
		await event.message.respond(reply)
	else:
		await event.message.respond("Invalid map command, can be `add`, `get`, `remove`, `list`.")

@command('cfg')
async def cfg_cmd(event:DMMessageCreateEvent, *args) -> None:
	if event.message.attachments and len(event.message.attachments) > 0:
		for att in event.message.attachments:
			if att.extension != "toml":
				await event.message.respond(f"`{att.filename}` is not a valid config file!")
			else:
				with open(CONFIG_PATH / 'config.toml', 'r') as fb:
					backup = fb.read()
				async with att.stream() as stream:
					data = await stream.read()
					with open(CONFIG_PATH / 'config.toml', 'wb') as fw:
						fw.write(data)
					await event.message.respond(f"Uploaded to `config/config.toml`.")
	elif args[1] == 'get':
		async with bot.rest.trigger_typing(event.channel_id):
			await event.message.respond("`config.toml`", attachment=CONFIG_PATH / 'config.toml')
	elif event.content: # useless check to make mypy shut up 
		config = toml.load(CONFIG_PATH / 'config.toml')
		try:
			cmd = event.content.replace('cfg ', '')
			change = toml.loads(cmd)
			config.update(change)
			with open(CONFIG_PATH / "config.toml", "w") as f:
				toml.dump(config, f)
			changedText = toml.dumps(change).rstrip('\n')
			await event.message.respond(f"`{changedText}` succesfully written to `config/config.toml`.")
		except toml.decoder.TomlDecodeError as e:
			logging.exception("Error while parsing TOML.")
			await event.message.respond(f"`{cmd}` was not a valid TOML expression.")

SERVER_ACTIONS = {
	'restart' : lambda c: c.restart(),
	'start' : lambda c: c.start(),
	'stop' : lambda c: c.kill(signal=SIGINT),
	'kill' : lambda c: c.kill(),
	'pause' : lambda c: c.pause(),
	'unpause' : lambda c: c.unpause(),
}

@command('server')
async def server_cmd(event:DMMessageCreateEvent, *args):
	client = docker.from_env()
	aos = client.containers.get(DOCKER_NAME)

	if args[1] == "status":
		await event.message.respond(f"Server is currently `{aos.status}`.")
	elif args[1] in ("log", "logs"):
		if event.author_id not in OWNER:
			return
		with open(CONFIG_PATH / 'latest.log', "wb") as f:
			f.write(aos.logs()) #This is so it has a file extension discord can embed
		async with bot.rest.trigger_typing(event.channel_id):
			await event.message.respond("`latest.log`", attachment=CONFIG_PATH / 'latest.log')
		os.remove(CONFIG_PATH / 'latest.log')
	elif args[1] in SERVER_ACTIONS:
		try:
			SERVER_ACTIONS[args[1]](aos)
			await event.message.respond(f"Action executed : `{args[1]}`")
		except docker.errors.APIError as e:
			logging.exception("Error while processing '%s'", args[1])
			await event.message.respond(f"Encountered an `APIError` while executing `{args[1]}`")
	else:
		await event.message.respond("Invalid server command, can be " + str.join(', ', (f'`{a}`' for a in (['status'] + list(SERVER_ACTIONS.keys())))) + '.')

bot.run()
