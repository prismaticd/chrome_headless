#!/usr/bin/env python

# Google cloud function entrypoint

import html_to_pdf.app


def main(request):
    return html_to_pdf.app.main(request)
