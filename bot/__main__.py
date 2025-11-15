from . import LOGGER, bot_loop
from .core.mltb_client import TgClient
from .core.config_manager import Config

Config.load()

async def main():
    from asyncio import gather
    from .core.startup import (
        load_settings,
        load_configurations,
        save_settings,
        update_aria2_options,
        update_nzb_options,
        update_qb_options,
        update_variables,
    )

    await load_settings()

    await gather(TgClient.start_bot(), TgClient.start_user())
    await gather(load_configurations(), update_variables())

    from .core.torrent_manager import TorrentManager

    await TorrentManager.initiate()
    await gather(
        update_qb_options(),
        update_aria2_options(),
        update_nzb_options(),
    )
    from .helper.ext_utils.files_utils import clean_all
    from .core.jdownloader_booter import jdownloader
    from .helper.ext_utils.telegraph_helper import telegraph
    from .helper.mirror_leech_utils.rclone_utils.serve import rclone_serve_booter
    from .modules import (
        initiate_search_tools,
        get_packages_version,
        restart_notification,
    )

    await gather(
        save_settings(),
        jdownloader.boot(),
        clean_all(),
        initiate_search_tools(),
        get_packages_version(),
        restart_notification(),
        telegraph.create_account(),
        rclone_serve_booter(),
    )

bot_loop.run_until_complete(main())

from .helper.ext_utils.bot_utils import create_help_buttons
from .helper.listeners.aria2_listener import add_aria2_callbacks
from .core.handlers import add_handlers

add_aria2_callbacks()
create_help_buttons()
add_handlers()

LOGGER.info("Bot Started!")

# Added: AioHTTP server for Koyeb health checks on port 8080
import asyncio
from aiohttp import web

async def health_check(request):
    return web.json_response({"status": "alive"})

async def start_aiohttp_server():
    app = web.Application()
    app.router.add_get('/', health_check)  # Responds to GET / with {"status": "alive"}
    app.router.add_get('/health', health_check)  # Optional: Also responds to /health
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)  # Bind to all interfaces on port 8080
    await site.start()
    LOGGER.info("AioHTTP server started on port 8080 for Koyeb health checks")
    # Keep the server running indefinitely
    while True:
        await asyncio.sleep(3600)  # Sleep to prevent blocking, but server stays active

# Run the aiohttp server in the background
bot_loop.create_task(start_aiohttp_server())

bot_loop.run_forever()
