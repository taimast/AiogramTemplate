import pytesseract
from PIL import Image

# If you don't have tesseract executable in your PATH, include the following:
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
file = open("screen.png", "rb")
# Simple image to string
image = Image.open(file)
print(pytesseract.image_to_string(
    image,
    # lang="rus"
))
