import asyncio
import os

import shutil
from datetime import datetime
from pathlib import Path
from pyppeteer import launch
from pyppeteer.errors import NetworkError

from ..utils import print_it

BROWSER = None


os.environ["PYPPETEER_HOME"] = os.path.join(
    os.path.dirname(__file__), "/tmp/PYPPETEER_HOME"
)

# local_chromium = Path(os.path.dirname(__file__)) / "local-chromium"
# # local_chromium.mkdir(exist_ok=True)
#
p = Path(os.environ["PYPPETEER_HOME"])
p.mkdir(exist_ok=True)
#
# l = p / "local-chromium"
# l.symlink_to(local_chromium)

from pyppeteer.chromium_downloader import (
    download_chromium,
    check_chromium,
    DOWNLOADS_FOLDER,
    REVISION,
)

if not check_chromium():
    download_chromium()

for child in Path(DOWNLOADS_FOLDER).iterdir():
    if not child.name == REVISION:
        folder = str(child.resolve())
        print("Found old chrome revision deleting: {}".format(folder))
        shutil.rmtree(folder)


async def get_blank_page():
    global BROWSER
    try:
        if not BROWSER or not BROWSER._connection._connected:
            if BROWSER:
                await BROWSER.close()
            BROWSER = await launch(args=["--no-sandbox"])
        page = await BROWSER.newPage()
    except NetworkError as e:
        print_it(e)
        await BROWSER.close()
        BROWSER = await launch(args=["--no-sandbox"])
        page = await BROWSER.newPage()

    return page


async def html_to_pdf(url, out_path, options=None):
    # Note that this needs to be async due to implementation of pyppeteer
    start = datetime.now()
    print_it("Starting HTML to pdf")
    page = await get_blank_page()
    await page.goto(url)

    await page.pdf(
        path=out_path,
        # pass in as dict instead of unpacking with ** so that explicit kwargs override instead of clash
        options=options,
    )
    await page.close()
    # shutdown browser at end of request to save memory at expense of startup time
    if os.environ.get("CHROMEHEADLESS_CLOSE_AFTER_REQUEST"):
        await BROWSER.close()
    print_it(f"Generated PDF in {datetime.now() - start} from {url}")
    return


def html_to_pdf_sync(url, out_path, options=None):
    """
    blocking wrapper around async renderer
    :param url:
    :param out_path:
    :param options:
    :return:
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
        loop = asyncio.get_event_loop()
    loop.run_until_complete(html_to_pdf(url, out_path, options))
