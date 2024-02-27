import asyncio
import re
import logging
import libtorrent as lt
from datetime import datetime
from colab_leecher.utility.helper import sizeUnit, status_bar
from colab_leecher.utility.variables import BOT, Aria2c, Paths, Messages, BotTimes


async def aria2c_Download(link: str, num: int):
    global BotTimes, Messages
    name_d = await get_Aria2c_Name(link)
    BotTimes.task_start = datetime.now()
    Messages.status_head = f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link {str(num).zfill(2)}</i>\n\n<b>🏷️ Name » </b><code>{name_d}</code>\n"
    
    try:
        ses = lt.session()
        ses.listen_on(6881, 6891)

        params = {"save_path": Paths.down_path}
        handle = lt.add_magnet_uri(ses, link, params)

        if not handle.is_valid():
            logging.error("Invalid magnet URI.")
            raise Exception("Invalid magnet URI.")

        while not handle.has_metadata():
            await asyncio.sleep(1)

        torrent_info = handle.get_torrent_info()
        name = torrent_info.name()

        while not handle.is_seed():
            s = handle.status()
            downloaded = s.total_download
            total = torrent_info.total_size()
            progress_percentage = downloaded / total * 100

            # Get download speed, ETA, etc.
            current_speed = s.download_rate
            eta = s.time_left
            downloaded_bytes = s.total_download
            total_size = torrent_info.total_size()  # Corrected
            elapsed_time_seconds = (datetime.now() - BotTimes.task_start).seconds
            percentage = progress_percentage

            speed_string = f"{sizeUnit(current_speed)}/s"
            await status_bar(
                Messages.status_head,
                speed_string,
                int(percentage),
                eta,
                downloaded_bytes,
                total_size,
                "libtorrent 🌩️",
            )

            # Update UI or log progress
            await asyncio.sleep(1)


async def get_Aria2c_Name(link):
    if len(BOT.Options.custom_name) != 0:
        return BOT.Options.custom_name
    ses = lt.session()
    handle = lt.add_magnet_uri(ses, link, {})
    while not handle.has_metadata():
        await asyncio.sleep(1)
    torrent_info = handle.get_torrent_info()
    name = torrent_info.name()
    if len(name) == 0:
        name = "UNKNOWN DOWNLOAD NAME"
    return name
