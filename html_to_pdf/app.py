import json
import logging
import os
import random
import string
from zipfile import ZipFile

from datetime import datetime
from flask import g, send_file
from werkzeug.utils import secure_filename

from .renderers import chrome_headless, weasyprint

logger = logging.getLogger(__name__)


def main(request):
    # request_json = request.get_json()
    url = request.args.get("url")
    if not url and request.method == "GET":
        return (
            """
        <html>
        <body>
            <p>
            POST to this url or add a ?url= param
            </p>
            <form action="" method="post"  enctype="multipart/form-data">
                <ul>
                    <li>
                        <input type="file" name="file" accept="zip">
                        <label for="file">zip containing HTML entrypoint, css, images etc</file>
                    </li>
                    <li>
                        <input type="text" name="entrypoint" value="index.html">
                        <label for="entrypoint">file to render within zip file</label>
                    </li>
                    <li>
                        <input type="radio" name="renderer" id="renderer_chrome" value="chrome" checked>
                        <label for="renderer_chrome">Chrome Headless</label>
                        <input type="radio" name="renderer" id="renderer_weasyprint" value="weasyprint">
                        <label for="renderer_weasyprint">Weasyprint</label>
                    </li>
                    <li>
                        <input type="textarea" name="options_json" value="{}">
                        <label for="options_json">options_json, as per 
                        <a href="https://miyakogi.github.io/pyppeteer/reference.html#pyppeteer.page.Page.pdf" target="_blank">pyppeteer PDF options</a></label>
                    </li>
                    <li>
                        <input type="submit" value="Upload">
                    </li>
                </ul>
            </form>
        </body>
        </html>
        """,
            200,
        )

    pdf_options = {}

    if request.method == "POST":
        renderer = request.form.get("renderer", "chrome")

        if "file" not in request.files:
            return "ERROR: No file part", 400
        file = request.files["file"]
        if file.filename == "":
            return "ERROR: No selected file", 400
        if file:
            pdf_options = json.loads(request.form.get("options_json", "{}"))
            entrypoint = request.form.get("entrypoint", "index.html")

            filename = secure_filename(file.filename)
            folder_name = "".join(
                random.choice(string.ascii_letters) for _ in range(10)
            )
            g.folder_path = f"/tmp/htmltopdf/{folder_name}"
            os.makedirs(g.folder_path, exist_ok=True)

            zip_location = os.path.join(g.folder_path, filename)
            file.save(zip_location)

            with ZipFile(zip_location, "r") as myzip:
                myzip.extractall(g.folder_path)

            url = f"file://{g.folder_path}/{entrypoint}"

        logger.info(f"Rendering {url} using {renderer}")
        pdf_path = f"{g.folder_path}/res.pdf"

        start = datetime.now()

        if renderer == "chrome":
            chrome_headless.html_to_pdf_sync(url, pdf_path, pdf_options)
        elif renderer == "weasyprint":
            weasyprint.html_to_pdf_sync(url, pdf_path, pdf_options)
        else:
            return "ERROR: invalid rendererer selected", 400

        logger.warning(f"Rendered in {datetime.now() - start} using {renderer}")

        return send_file(pdf_path, attachment_filename="file.pdf"), 200

    return "Error", 400
