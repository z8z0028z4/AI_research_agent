"""
DOCX Generation Utilities
=========================

Helper functions for generating DOCX files, including text cleaning and image handling.
"""

import io
import os
import re
import tempfile
import time
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from io import BytesIO

# SVG conversion dependencies
try:
    from svglib.svglib import svg2rlg
    from reportlab.graphics import renderPDF
    SVGLIB_AVAILABLE = True
except ImportError:
    SVGLIB_AVAILABLE = False

# PyMuPDF for PDF to PNG conversion
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


def clean_text_for_xml(text):
    """Cleans text to ensure XML compatibility."""
    if not text:
        return ""
    # Remove NULL bytes and control characters
    cleaned = "".join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    # Remove other characters that could cause XML issues
    cleaned = cleaned.replace('\x00', '')  # NULL byte
    cleaned = cleaned.replace('\x01', '')  # SOH
    cleaned = cleaned.replace('\x02', '')  # STX
    cleaned = cleaned.replace('\x03', '')  # ETX
    cleaned = cleaned.replace('\x04', '')  # EOT
    cleaned = cleaned.replace('\x05', '')  # ENQ
    cleaned = cleaned.replace('\x06', '')  # ACK
    cleaned = cleaned.replace('\x07', '')  # BEL
    cleaned = cleaned.replace('\x08', '')  # BS
    cleaned = cleaned.replace('\x0b', '')  # VT
    cleaned = cleaned.replace('\x0c', '')  # FF
    cleaned = cleaned.replace('\x0e', '')  # SO
    cleaned = cleaned.replace('\x0f', '')  # SI
    return cleaned

def clean_markdown_text(text):
    """Cleans markdown formatting, converting it to plain text."""
    if not text:
        return ""

    # Remove markdown formatting
    cleaned = text
    cleaned = re.sub(r'\*\*(.*?)\*\*', r'\1', cleaned)  # Remove bold
    cleaned = re.sub(r'\*(.*?)\*', r'\1', cleaned)  # Remove italic
    cleaned = re.sub(r'`(.*?)`', r'\1', cleaned)  # Remove code
    cleaned = re.sub(r'^#+\s*(.*)$', r'\1', cleaned, flags=re.MULTILINE)  # Remove headers
    cleaned = re.sub(r'^\s*[-*+]\s+', '- ', cleaned, flags=re.MULTILINE)  # Unify list bullets
    cleaned = re.sub(r'^\s*\d+\.\s+', '', cleaned, flags=re.MULTILINE)  # Remove numbered lists
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)  # Remove extra blank lines
    cleaned = re.sub(r'\n\s*\*\*', '\n', cleaned)  # Remove newlines before bold
    cleaned = re.sub(r'\*\*\s*\n', '\n', cleaned)  # Remove newlines after bold

    return cleaned

def get_image_stream_from_url(url: str) -> BytesIO | None:
    """Downloads an image from a URL and returns a BytesIO stream."""
    if not url:
        return None
    try:
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            print(f"⚠️ Image download failed with status {response.status_code}: {url}")
            return None
    except Exception as e:
        print(f"⚠️ Image download failed: {url}, {e}")
        return None

def get_ghs_icon_stream(icon_url: str) -> BytesIO | None:
    """Downloads a GHS icon, converts it from SVG to PNG if necessary, and returns a BytesIO stream."""
    if not icon_url:
        return None

    try:
        icon_resp = requests.get(icon_url, verify=False, timeout=5)
        if icon_resp.status_code != 200:
            return None

        if not (SVGLIB_AVAILABLE and PYMUPDF_AVAILABLE):
            print(f"⚠️ svglib or PyMuPDF not available, cannot convert SVG: {icon_url}")
            return None

        drawing = svg2rlg(io.BytesIO(icon_resp.content))
        if not drawing:
            print(f"⚠️ SVG conversion failed - drawing is None: {icon_url}")
            return None

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            renderPDF.drawToFile(drawing, tmp_pdf.name)

        pdf_document = fitz.open(tmp_pdf.name)
        page = pdf_document[0]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))

        png_stream = io.BytesIO()
        png_stream.write(pix.tobytes("png"))
        png_stream.seek(0)

        pdf_document.close()
        os.unlink(tmp_pdf.name)

        return png_stream
    except Exception as e:
        print(f"⚠️ Failed to convert or insert icon: {icon_url}, {e}")
        return None


def get_nfpa_icon_image_stream(nfpa_code: str) -> BytesIO:
    """
    Fetches an NFPA icon from PubChem using a headless Chrome browser and returns a PNG BytesIO stream.
    """
    nfpa_svg_url = f"https://pubchem.ncbi.nlm.nih.gov/image/nfpa.cgi?code={nfpa_code}"

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=300,300")
    chrome_options.add_argument("--hide-scrollbars")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(nfpa_svg_url)
    time.sleep(1)

    png_data = driver.get_screenshot_as_png()
    driver.quit()

    image = Image.open(io.BytesIO(png_data))
    cropped = image.crop((0, 0, 100, 100))
    output = io.BytesIO()
    cropped.save(output, format="PNG")
    output.seek(0)
    return output
