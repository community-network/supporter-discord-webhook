import asyncio
import json
import aiohttp
from quart import Quart
from hypercorn.config import Config
from hypercorn.asyncio import serve
from quart import request

app = Quart(__name__)

@app.route("/", methods=["POST"])
async def webhook():
    webhook_id = request.args.get("webhook_id")
    webhook_auth = request.args.get("webhook_auth")

    color = request.args.get("color")
    if color is None:
        color = 222934

    data = await request.get_json()
    try:
        if data["action"] == "created":
            sponsorship = data["sponsorship"]
            tier_description = sponsorship["tier"]["description"]
            username = sponsorship["sponsor"]["login"]
            price_in_dollars = int(sponsorship["tier"]["monthly_price_in_cents"])/100
            supporter_url_html = sponsorship["sponsor"]["html_url"]
            supporter_icon = sponsorship["sponsor"]["avatar_url"]
            webhook_send_json = {
                "embeds": [
                    {
                        "description": f"{tier_description}",
                        "color": color,
                        "author": {
                            "name": f"{username} just sponsored for ${price_in_dollars}",
                            "url": f"{supporter_url_html}",
                            "icon_url": f"{supporter_icon}"
                        },
                        "footer": {
                            "text": "Thank you for supporting us, it really helps out"
                        }
                    }
                ]
            }
            async with aiohttp.ClientSession() as session:
                await session.post(f"https://discordapp.com/api/webhooks/{webhook_id}/{webhook_auth}", data=webhook_send_json)
                return "Successfully sent webhook to discord!"
    except Exception as e:
        if data["hook"]["type"] == "SponsorsListing":
            send_json = {
                "content": "Github sponsor webhooks have now been added."
            }
            async with aiohttp.ClientSession() as session:
                test = await session.post(f"https://discordapp.com/api/webhooks/{webhook_id}/{webhook_auth}", data=send_json)
                print(test)
                return "Setup complete! You will now receive notifications when someone supports you on github!"
        else:
            return e


@app.route("/healthcheck")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    config = Config.from_mapping(
            bind="0.0.0.0:5053",
            statsd_host="0.0.0.0:5053",
        )
    asyncio.run(serve(app, config))