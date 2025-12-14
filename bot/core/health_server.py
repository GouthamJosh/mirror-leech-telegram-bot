import os
from aiohttp import web

async def health(request):
    return web.Response(text="OK", status=200)

async def start_health_server():
    app = web.Application()
    app.router.add_get("/", health)
    app.router.add_get("/health", health)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 8000))  # Koyeb uses PORT
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
