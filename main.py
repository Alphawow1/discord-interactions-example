#!/usr/bin/env python

from discord_interactions.flask_ext import Interactions, CommandContext, AfterCommandContext
from discord_interactions import Member
from flask import Flask
import os
import random
from commands import Ping, Echo, RPS, RPSSymbol, Guess, Delay, Hug, UserInfo
import time
import json

app = Flask(__name__)
interactions = Interactions(app, os.getenv("0f8ab6334fbbe0ec9ee562fd5a43ea1e8a80e8b52cc7734037897ea3b09e9d39"), os.getenv("1250512173491294259"))

PUBLIC_KEY = os.getenv("0f8ab6334fbbe0ec9ee562fd5a43ea1e8a80e8b52cc7734037897ea3b09e9d39")

# Verify Discord request
# Verify Discord request
def verify_request(req):
    try:
        signature = req.headers['X-Signature-Ed25519']
        timestamp = req.headers['X-Signature-Timestamp']
        body = req.data.decode('utf-8')
        message = timestamp + body
        verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
        verify_key.verify(message.encode(), bytes.fromhex(signature))
    except (BadSignatureError, KeyError) as e:
        logging.error(f"Request verification failed: {e}")
        return False
    return True

@app.route('/', methods=['POST'])
def index():
    logging.info("Received a request")
    if not verify_request(request):
        logging.warning("Invalid request signature")
        return jsonify({"error": "Invalid request signature"}), 401
    
    data = request.json
    logging.debug(f"Request data: {data}")
    if data['type'] == 1:  # PING request
        logging.info("Responding to PING request")
        return jsonify({"type": 1})
    
    # Handle other interaction types
    # Here you can handle your command logic

    logging.error("Unknown interaction type")
    return jsonify({"error": "Unknown interaction type"}), 400
    

@interactions.command
def ping(_: Ping):
    return "pong"

@interactions.command
def echo(cmd: Echo):
    return cmd.message, False

@interactions.command
def rps(cmd: RPS):
    choice = random.choice(list(RPSSymbol))
    if cmd.symbol == choice:
        msg = "It's a draw!"
    elif cmd.symbol == RPSSymbol.ROCK:
        if choice == RPSSymbol.SCISSORS:
            msg = "You crush me and win!"
        else:
            msg = "You get covered and lose!"
    elif cmd.symbol == RPSSymbol.PAPER:
        if choice == RPSSymbol.ROCK:
            msg = "You cover me and win!"
        else:
            msg = "You get cut and lose!"
    else:
        if choice == RPSSymbol.ROCK:
            msg = "You get crushed and lose!"
        else:
            msg = "You cut me and win!"
    return f"I took {choice.value}. {msg}"

@interactions.command(Guess)
def guess(_: CommandContext, guessed_num, min_num=None, max_num=None):
    min_val = min_num or 0
    max_val = max_num or 10
    my_number = random.randint(min_val, max_val)
    if my_number == guessed_num:
        msg = "You are correct! :tada:"
    else:
        msg = "You guessed it wrong. :confused:"
    return f"My number was {my_number}. {msg}"

@interactions.command(Delay)
def delay(_):
    return None

@delay.after_command
def after_delay(ctx: AfterCommandContext):
    delay_time = ctx.interaction.data.options[0].value
    time.sleep(delay_time)
    ctx.edit_original(f"{delay_time} seconds have passed")

@interactions.command
def hug(cmd: Hug):
    return f"<@{cmd.interaction.author.id}> *hugs* <@{cmd.cutie}>"

@interactions.command
def user_info(cmd: UserInfo):
    u_id = cmd.user
    if u_id:
        member = cmd.interaction.get_member(u_id)
        user = cmd.interaction.get_user(u_id)
        if member:
            member.user = user
            user = member
    else:
        user = cmd.author
    if cmd.raw:
        return f"```json\n{json.dumps(user.to_dict(), indent=2)}\n```", True
    info = ""
    if isinstance(user, Member):
        role_info = " ".join(f"<@&{r}>" for r in user.roles)
        info += f"**Member**\nnick: `{user.nick}`\nroles: {role_info}\njoined at: `{user.joined_at.isoformat()}`\n"
        if user.premium_since:
            info += f"premium since: `{user.premium_since.isoformat()}`\n"
        info += f"deaf: `{user.deaf}`\nmute: `{user.mute}`\npending: `{user.pending}`\n\n"
        user = user.user
    info += f"**User**\nid: `{user.id}`\nusername: `{user.username}`\ndiscriminator: `{user.discriminator}`\navatar: `{user.avatar}`\npublic flags: {', '.join(f'`{f.name}`' for f in user.public_flags)}"
    return info, True

if __name__ == "__main__":
    app.run("0.0.0.0", port=int(os.getenv("PORT", 5000)))
