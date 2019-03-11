import json
import os
import random
import string
from zipfile import ZipFile

from flask import g, send_file
from werkzeug.utils import secure_filename

from .renderers import chrome_headless
from .utils import print_it


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
        if "file" not in request.files:
            print_it(request.files)
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
            print_it(url)

        print_it(f"Rendering {url}")
        pdf_path = f"{g.folder_path}/res.pdf"

        if True:
            chrome_headless.html_to_pdf_sync(url, pdf_path, pdf_options)

        return send_file(pdf_path, attachment_filename="file.pdf"), 200

    return "Error", 400
