from tempfile import TemporaryDirectory
 
import pytesseract
from pdf2image import convert_from_path
from PIL import Image

from tinydb import TinyDB
 
language = 'hin'
 
def to_english(input_file, output_file):
    image_file_list = []

    with TemporaryDirectory() as tempdir:
        pdf_pages = convert_from_path(input_file, 500)

        for page_enumeration, page in enumerate(pdf_pages, start=1):
            filename = f"{tempdir}/page_{page_enumeration}.jpg"
            page.save(filename, "JPEG")
            image_file_list.append(filename)
 
        with open(output_file, "a") as h:
            for image_file in image_file_list:
                text = str(((pytesseract.image_to_string(Image.open(image_file), lang=language))))
 
                # In many PDFs, at line ending, if a word can't
                # be written fully, a 'hyphen' is added.
                # The rest of the word is written in the next line
                # Eg: This is a sample text this word here GeeksF-
                # orGeeks is half on first line, remaining on next.
                # To remove this, we replace every '-\n' to ''.
                text = text.replace("-\n", "")

                breakpoint()
 
                h.write(text)

db = TinyDB('orders.json')
entries = db.all()

for entry in entries:
    to_english(entry['filename'], f'translated/{entry["filename"][4:-4]}.txt')
