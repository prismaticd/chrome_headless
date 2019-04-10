import logging

from weasyprint import HTML

logger = logging.getLogger(__name__)


def html_to_pdf_sync(url, out_path, options=None):
    HTML(url).write_pdf(out_path)
