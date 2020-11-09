import websockets
import json
import asyncio
import ssl
import logging as log
import lib
from sys import exc_info as exc
from yaml import safe_load
from mysql.connector import connect as dbconnect

log.basicConfig(
    filename="node.log",
    format="Node @ %(asctime)s | %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=log.INFO,
)

loop = asyncio.get_event_loop()
config = safe_load(open("config.yml", "r"))
db = dbconnect(
    host=config["Database"]["Host"],
    port=config["Database"]["Port"],
    user=config["Database"]["Username"],
    password=config["Database"]["Password"],
    database="aerial",
)
db.autocommit = True
c = db.cursor()
c.execute(
    """UPDATE `accounts` SET `in_use` = '0' WHERE `id` >= '%s' AND `id` <= '%s';"""
    % (config["Database"]["Pool_Start"], config["Database"]["Pool_End"])
)
c.close()
del c


# Main WebSocket Handler
async def wshandle(ws, path):
    if ws.remote_address[0] not in config["Allowed_IPs"]:
        log.warning("Denied WebSocket Connection from " + ws.remote_address[0])
        await ws.close(code=4000, reason="Unauthorized")
        return
    log.info("Established WebSocket Connection")
    c = db.cursor()
    c.execute(
        """SELECT * FROM `accounts` WHERE `in_use` = '0' AND `id` >= '%s' AND `id` <= '%s' ORDER BY RAND() LIMIT 1;"""
        % (config["Database"]["Pool_Start"], config["Database"]["Pool_End"])
    )
    details = c.fetchone()
    if details is None:
        await ws.send(json.dumps({"type": "no_free_accounts"}))
        log.info("Closed WebSocket Connection - No Free Accounts")
        await ws.close(code=1000, reason="No Free Accounts")
        return
    c.execute(
        """UPDATE `accounts` SET `in_use` = '1' WHERE `id` = '%s';""" % details[0]
    )
    bot = lib.Client(
        {
            "device_id": details[3],
            "account_id": details[4],
            "secret": details[5],
        },
        ws,
    )
    log.info(f"Took Account {details[0]}")
    loop.create_task(bot.start())
    await bot.wait_until_ready()
    await ws.send(
        json.dumps(
            {
                "type": "account_info",
                "username": bot.user.display_name,
                "outfit": "CID_565_Athena_Commando_F_RockClimber",
            }
        )
    )
    loop.create_task(lib.delay_stop(bot, 10800))
    try:
        async for message in ws:
            log.info(f"Received Message for {details[0]}: {message}")
            try:
                await lib.process(bot, json.loads(message))
            except:
                log.error(
                    f"Exception Whilst Processing for {details[0]}: {exc()[0]} {exc()[1]} {exc()[2]}"
                )
    except:
        pass
    log.info("Closed WebSocket Connection")
    log.info(f"Shutting Down Account {details[0]}")
    await bot.close()
    c.execute(
        """UPDATE `accounts` SET `in_use` = '0' WHERE `id` = '%s';""" % details[0]
    )
    db.commit()
    c.close()
    log.info(f"Freed Account {details[0]}")
    del details
    del bot
    del c


async def start():
    await websockets.server.serve(
        wshandle,
        "0.0.0.0",
        8765,
        ssl=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER).load_cert_chain(
            certfile="ssl/cert.pem", keyfile="ssl/key.pem"
        ),
        ping_interval=10,
        ping_timeout=10
    )


loop.create_task(start())
loop.run_forever()
