import logging
import re
from datetime import datetime

import libtorrent as lt

from colab_leecher.utility.helper import sizeUnit, status_bar
from colab_leecher.utility.variables import BOT, Aria2c, Paths, Messages, BotTimes


async def aria2_download(link: str, num: int):
    global BotTimes, Messages
    name_d = get_aria2c_name(link)
    BotTimes.task_start = datetime.now()
    Messages.status_head = (
        f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link {str(num).zfill(2)}</i>\n\n"
        f"<b>🏷️ Name » </b><code>{name_d}</code>\n"
    )

    ses = lt.session()
    ses.listen_on(6881, 6891)
    params = {
        "save_path": Paths.down_path,
        "storage_mode": lt.storage_mode_t.storage_mode_sparse,
        "url": link,
    }

    handle = ses.add_torrent(params)
    ses.start_dht()

    handle.set_max_connections(60)
    handle.set_max_uploads(-1)

    await on_download_started()

    while not handle.is_seed():
        await on_download_progress(handle.status())

    await on_download_complete()
    logging.info("Download complete")


def get_aria2c_name(link):
    if len(BOT.Options.custom_name) != 0:
        return BOT.Options.custom_name
    # You might need to adjust this part based on libtorrent's API for fetching the name
    return "UNKNOWN DOWNLOAD NAME"


async def on_download_started():
    logging.info("Download started")


async def on_download_progress(status):
    total_size = status.total_wanted
    downloaded_bytes = status.total_wanted_done
    progress_percentage = downloaded_bytes / total_size * 100 if total_size != 0 else 0
    eta = status.next_announce.total_seconds() if status.next_announce else 0
    current_speed = status.download_rate
    speed_string = f"{sizeUnit(current_speed)}/s"

    await status_bar(
        Messages.status_head,
        speed_string,
        int(progress_percentage),
        eta,
        str(downloaded_bytes),
        str(total_size),
        "Aria2c 🧨",
    )


async def on_download_complete():
    logging.info("Download complete")
    # Add any additional actions you want to perform after download completion here
