import os
import easyocr
import shutil
import csv
from pdf2image import convert_from_path
# import pytesseract
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_csv_filenames(csv_path):
    filenames = set()
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) >= 4:
                filename = row[4].strip()
                if filename.lower().endswith('.pdf'):
                    filenames.add(filename)
    return filenames

def process_pdf(pdf_path, output_folder, dpi=300, lang='hi'):
    reader = easyocr.Reader(['hi'], gpu=True)  # 'hi' is for Hindi
    pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
    pdf_output_dir = os.path.join(output_folder, pdf_name)
    images_dir = os.path.join(pdf_output_dir, "images")

    os.makedirs(images_dir, exist_ok=True)

    try:
        images = convert_from_path(pdf_path, dpi=dpi)
        ocr_texts = []

        for i, image in enumerate(images):
            image_path = os.path.join(images_dir, f"page_{i+1}.png")
            image.save(image_path, "PNG")

            # GPU-accelerated OCR
            result = reader.readtext(image_path, detail=0)
            text = "\n".join(result)

            ocr_texts.append(f"--- Page {i+1} ---\n{text.strip()}\n")

        ocr_output_path = os.path.join(pdf_output_dir, "ocr_output.txt")
        with open(ocr_output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ocr_texts))

        print(f"✅ Processed with GPU: {pdf_path} → {ocr_output_path}")
    except Exception as e:
        print(f"❌ Error processing {pdf_path}: {e}")

def collect_txt_files(base_output_folder, destination_folder):
    os.makedirs(destination_folder, exist_ok=True)
    for root, dirs, files in os.walk(base_output_folder):
        for file in files:
            if file == "ocr_output.txt":
                full_path = os.path.join(root, file)
                new_name = os.path.basename(os.path.dirname(full_path)) + ".txt"
                dest_path = os.path.join(destination_folder, new_name)
                shutil.copy(full_path, dest_path)
                print(f"📁 Copied: {full_path} → {dest_path}")

def batch_process_folder(input_folder, output_folder, csv_path, dpi=300, lang='hi', max_threads=32):
    os.makedirs(output_folder, exist_ok=True)

    # Read allowed filenames from the CSV
    valid_filenames = read_csv_filenames(csv_path)

    # Only include matching PDF files
    pdf_files = [
        os.path.join(input_folder, filename)
        for filename in os.listdir(input_folder)
        if filename in valid_filenames
    ]

    print(f'number_of_files: {len(pdf_files)}')

    if not pdf_files:
        print("⚠️ No matching PDF files found in input folder.")
        return

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(process_pdf, pdf_path, output_folder, dpi, lang): pdf_path
            for pdf_path in pdf_files
        }

        for future in as_completed(futures):
            pdf_path = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"⚠️ Failed to process {pdf_path}: {e}")

    # collect_txt_files(output_folder, os.path.join(output_folder, "all_texts"))

# Set your actual folders and CSV path
input_folder = "pdf"
output_folder = "transcribed"
csv_path = "files.csv"

# Run batch processing with CSV filtering
# batch_process_folder(input_folder, output_folder, csv_path, lang='hin', max_threads=2)
collect_txt_files(output_folder, os.path.join(output_folder, "all_texts"))
