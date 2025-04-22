import os
import csv
import re
import argostranslate.translate

# Load Argos Translate model (assumes it's already installed)
installed_languages = argostranslate.translate.load_installed_languages()
hi_lang = next(filter(lambda x: x.code == "hi", installed_languages))
en_lang = next(filter(lambda x: x.code == "en", installed_languages))
translator = hi_lang.get_translation(en_lang)

# Hindi phrases to search
phrases = [
    "किशोर",
    "किशोर न्यायालय",
    "बोर्ड",
    "प्रारंभिक आकलन",
    "प्रारंभिक निर्धारण",
    "बालक"
]

main_phrases = ["किशोर", "किशोर न्यायालय"]

input_dir = "txt"
output_csv_hindi = "output_hindi.csv"
output_csv_english = "output_english.csv"
base_url = "https://aarch.compromyse.xyz:8000/txt/"

# Extract up to 10 snippets for a phrase
def extract_snippets(text, phrase, window=10, max_count=10):
    words = text.split()
    snippets = []
    for i, word in enumerate(words):
        if phrase in word:
            start = max(0, i - window)
            end = min(len(words), i + window + 1)
            snippet = ' '.join(words[start:end])
            snippets.append(snippet)
            if len(snippets) >= max_count:
                break
    return snippets

# CSV header
header = ["File", "File URL"]
for phrase in phrases:
    header.append(f"{phrase} Present")
    if phrase in main_phrases:
        for i in range(1, 11):
            header.append(f"{phrase} Snippet {i}")
    else:
        header.append(f"{phrase} Snippet")

# Process files
results = []
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        filepath = os.path.join(input_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            file_url = base_url + filename
            row = [filename, file_url]

            for phrase in phrases:
                found = phrase in text
                row.append("Yes" if found else "No")

                if found:
                    snippets = extract_snippets(text, phrase, max_count=10)
                    if phrase in main_phrases:
                        row.extend(snippets + [""] * (10 - len(snippets)))
                    else:
                        row.append(snippets[0] if snippets else "")
                else:
                    if phrase in main_phrases:
                        row.extend([""] * 10)
                    else:
                        row.append("")
            results.append(row)

# Write Hindi CSV
with open(output_csv_hindi, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(results)

# Translate header
translated_header = [translator.translate(cell) if re.search(r'[\u0900-\u097F]', cell) else cell for cell in header]

# Translate rows
translated_rows = [translated_header]
for row in results:
    translated_row = []
    for cell in row:
        try:
            if re.search(r'[\u0900-\u097F]', cell):  # Only translate if Hindi detected
                translated_row.append(translator.translate(cell))
            else:
                translated_row.append(cell)
        except:
            translated_row.append(cell)
    translated_rows.append(translated_row)

# Write English CSV
with open(output_csv_english, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(translated_rows)

print(f"✅ Hindi CSV saved to: {output_csv_hindi}")
print(f"✅ English CSV saved to: {output_csv_english}")
