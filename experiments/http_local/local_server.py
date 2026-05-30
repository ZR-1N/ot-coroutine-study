import asyncio
from aiohttp import web


async def handle_ping(request: web.Request) -> web.Response:
    delay_ms = int(request.query.get("delay_ms", "50"))
    await asyncio.sleep(delay_ms / 1000)
    return web.json_response({
        "ok": True,
        "delay_ms": delay_ms
    })


def main():
    app = web.Application()
    app.router.add_get("/ping", handle_ping)
    web.run_app(app, host="127.0.0.1", port=8080)


if __name__ == "__main__":
    main()