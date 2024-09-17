# copyright 2024 © KavinduAJ | https://github.com/kjeymax

import logging
import re
import asyncio
from datetime import datetime

import libtorrent as lt

from colab_leecher.utility.helper import sizeUnit, status_bar
from colab_leecher.utility.variables import BOT, Libtorrent, Paths, Messages, BotTimes


async def libtorrent_Download(link: str, num: int):
    global BotTimes, Messages
    name_d = await get_Libtorrent_Name(link)
    BotTimes.task_start = datetime.now()
    Messages.status_head = (
        f"<b>📥 DOWNLOADING FROM » </b><i>🔗Link {str(num).zfill(2)}</i>\n\n"
        f"<b>🏷️ Name » </b><code>{name_d}</code>\n"
    )

    ses = lt.session()
    ses.listen_on(6881, 6891)

    # Full list of trackers
    trackers = [
        "http://1337.abcvg.info:80/announce",
        "http://bt.okmp3.ru:2710/announce",
        "http://bvarf.tracker.sh:2086/announce",
        "http://ipv6.rer.lol:6969/announce",
        "http://jvavav.com:80/announce",
        "http://nyaa.tracker.wf:7777/announce",
        "http://retracker.x2k.ru:80/announce",
        "http://t.nyaatracker.com:80/announce",
        "http://t1.aag.moe:17715/announce",
        "http://taciturn-shadow.spb.ru:6969/announce",
        "http://tk.greedland.net:80/announce",
        "http://torrentsmd.com:8080/announce",
        "http://tr.kxmp.cf:80/announce",
        "http://tracker.bt4g.com:2095/announce",
        "http://tracker.dump.cl:6969/announce",
        "http://tracker.electro-torrent.pl:80/announce",
        "http://tracker.files.fm:6969/announce",
        "http://tracker.ipv6tracker.org:80/announce",
        "http://tracker.k.vu:6969/announce",
        "http://tracker.tfile.co:80/announce",
        "http://tracker2.itzmx.com:6961/announce",
        "http://www.all4nothin.net:80/announce.php",
        "http://www.wareztorrent.com:80/announce",
        "https://1337.abcvg.info:443/announce",
        "https://pybittrack.retiolus.net:443/announce",
        "https://tr.abir.ga:443/announce",
        "https://tr.burnabyhighstar.com:443/announce",
        "https://tracker.gcrenwp.top:443/announce",
        "https://tracker.itscraftsoftware.my.id:443/announce",
        "https://tracker.kuroy.me:443/announce",
        "https://tracker.lilithraws.org:443/announce",
        "https://tracker.tamersunion.org:443/announce",
        "https://tracker.yemekyedim.com:443/announce",
        "https://tracker1.520.jp:443/announce",
        "https://trackers.run:443/announce",
        "udp://amigacity.xyz:6969/announce",
        "udp://bandito.byterunner.io:6969/announce",
        "udp://bt2.archive.org:6969/announce",
        "udp://d40969.acod.regrucolo.ru:6969/announce",
        "udp://ec2-18-191-163-220.us-east-2.compute.amazonaws.com:6969/announce",
        "udp://evan.im:6969/announce",
        "udp://exodus.desync.com:6969/announce",
        "udp://isk.richardsw.club:6969/announce",
        "udp://leet-tracker.moe:1337/announce",
        "udp://martin-gebhardt.eu:25/announce",
        "udp://moonburrow.club:6969/announce",
        "udp://ns575949.ip-51-222-82.net:6969/announce",
        "udp://odd-hd.fr:6969/announce",
        "udp://open.demonii.com:1337/announce",
        "udp://open.stealth.si:80/announce",
        "udp://open.tracker.ink:6969/announce",
        "udp://opentor.org:2710/announce",
        "udp://opentracker.io:6969/announce",
        "udp://p4p.arenabg.com:1337/announce",
        "udp://retracker.hotplug.ru:2710/announce",
        "udp://retracker01-msk-virt.corbina.net:80/announce",
        "udp://run.publictracker.xyz:6969/announce",
        "udp://seedpeer.net:6969/announce",
        "udp://serpb.vpsburti.com:6969/announce",
        "udp://thetracker.org:80/announce",
        "udp://tk2.trackerservers.com:8080/announce",
        "udp://tracker.0x7c0.com:6969/announce",
        "udp://tracker.birkenwald.de:6969/announce",
        "udp://tracker.bittor.pw:1337/announce",
        "udp://tracker.breizh.pm:6969/announce",
        "udp://tracker.cyberia.is:6969/announce",
        "udp://tracker.darkness.services:6969/announce",
        "udp://tracker.dler.com:6969/announce",
        "udp://tracker.doko.moe:6969/announce",
        "udp://tracker.dump.cl:6969/announce",
        "udp://tracker.filemail.com:6969/announce",
        "udp://tracker.fnix.net:6969/announce",
        "udp://tracker.gmi.gd:6969/announce",
        "udp://tracker.opentrackr.org:1337/announce",
        "udp://tracker.skynetcloud.site:6969/announce",
        "udp://tracker.skyts.net:6969/announce",
        "udp://tracker.torrent.eu.org:451/announce",
        "udp://tracker.tryhackx.org:6969/announce",
        "udp://ttk2.nbaonlineservice.com:6969/announce",
        "udp://z.mercax.com:53/announce",
        "wss://tracker.openwebtorrent.com:443/announce"
    ]

    params = {
        "save_path": Paths.down_path,
        "storage_mode": lt.storage_mode_t.storage_mode_sparse,
        "trackers": trackers  # Adding all the provided trackers to the download session
    }

    if link.startswith("magnet:"):
        params["url"] = link
    elif link.startswith(("http://", "https://")):
        params["url"] = lt.parse_magnet_uri(link).url
    else:
        logging.error("Unsupported URI protocol.")
        return

    handle = ses.add_torrent(params)
    ses.start_dht()

    handle.set_max_connections(60)
    handle.set_max_uploads(-1)

    await on_download_started()

    while not handle.is_seed():
        await on_download_progress(handle.status())

        # Allow other tasks to run (prevents blocking the event loop)
        await asyncio.sleep(1)

    await on_download_complete()
    logging.info("Stay Tuned ⌛️")




async def get_Libtorrent_Name(link):
    if len(BOT.Options.custom_name) != 0:
        return BOT.Options.custom_name
    
    try:
        info = lt.torrent_info(link)
        return info.name()
    except Exception as e:
        logging.error(f"Failed to fetch torrent name: {e}")
        return "Unkown Download Name 🤷‍♂️"


async def on_download_started():
    logging.info("Download started 😀")


async def on_download_progress(status):
    total_size = status.total_wanted
    downloaded_bytes = status.total_wanted_done
    progress_percentage = downloaded_bytes / total_size * 100 if total_size != 0 else 0
    eta = status.next_announce.total_seconds() if status.next_announce else 0
    current_speed = status.download_rate
    speed_string = f"{sizeUnit(current_speed)}/s"

    # Convert total size and downloaded bytes to human-readable format
    total_size_hr = sizeUnit(total_size)
    downloaded_bytes_hr = sizeUnit(downloaded_bytes)

    await status_bar(
        Messages.status_head,
        speed_string,
        int(progress_percentage),
        eta,
        downloaded_bytes_hr,
        total_size_hr,
        "LIBT 🧲",
    )


def sizeUnit(size):
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    return f"{size:.2f} {units[unit_index]}"


async def on_download_complete():
    logging.info("Download complete ✅")
    # Add any additional actions you want to perform after download completion here
