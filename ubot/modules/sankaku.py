# SPDX-License-Identifier: GPL-2.0-or-later

from ubot.micro_bot import ldr

SAN_URL = "https://capi-v2.sankakucomplex.com/posts"
SAN_SAUCE_URL = "https://beta.sankakucomplex.com/post/show/"


@ldr.add("san(s|x|q|)(f|)")
async def sankaku(event):
    await event.edit(f"`Processing…`")
    safety_arg = event.pattern_match.group(1)
    as_file = bool(event.pattern_match.group(2))
    rating = ""

    if safety_arg == "x":
        rating = "rating:explicit"
    elif safety_arg == "s":
        rating = "rating:safe"
    elif safety_arg == "q":
        rating = "rating:questionable"

    params = {"page": 1,
              "limit": 5,
              "tags": f"order:random {rating} {event.args}".strip().replace("  ", " ")}

    async with ldr.aioclient.get(SAN_URL, params=params) as response:
        if response.status == 200:
            response = await response.json()
        else:
            await event.edit(f"`An error occurred, response code: `**{response.status}**")
            return

    if not response:
        await event.edit(f"`No results for query: `**{event.args}**")
        return

    valid_urls = []

    for post in response:
        if 'file_url' in post.keys():
            valid_urls.append([post['file_url'], post['id']])

    if not valid_urls:
        await event.edit(f"`Failed to find URLs for query: `**{event.args}**")
        return

    for image in valid_urls:
        try:
            await event.client.send_message(event.chat_id, f"[sauce]({SAN_SAUCE_URL}{image[1]})", file=image[0], force_document=as_file)
            await event.delete()
            return
        except:
            pass

    await event.edit(f"`Failed to fetch media for query: `**{event.args}**")
