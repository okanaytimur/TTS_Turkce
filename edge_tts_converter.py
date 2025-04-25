import os
import sys
import pathlib
import asyncio
from ebooklib import epub
from docx import Document
from bs4 import BeautifulSoup
from edge_tts import Communicate

OUTPUT_DIR = "output"
CHUNK_SIZE = 5000  # Edge-TTS sınırı yaklaşık 5000 karakter civarında

def extract_text_from_epub(file_path):
    book = epub.read_epub(file_path)
    text = ""
    for item in book.get_items():
        if item.get_type() == 9:  # ITEM_DOCUMENT
            content = item.get_content().decode("utf-8")
            soup = BeautifulSoup(content, "html.parser")
            text += soup.get_text() + "\n"
    return text

def extract_text_from_docx(file_path):
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

def split_text(text, max_length):
    chunks = []
    while len(text) > max_length:
        split_at = text.rfind('.', 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at + 1])
        text = text[split_at + 1:]
    chunks.append(text)
    return chunks
    
def format_ssml(text):
    sentences = text.strip().split('.')
    ssml = "<speak>"
    for sentence in sentences:
        clean = sentence.strip()
        if clean:
            ssml += f"{clean}"
    ssml += "</speak>"
    return ssml


async def convert_to_speech(chunks, voice="tr-TR-EmelNeural"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i, chunk in enumerate(chunks):
        ssml_text = format_ssml(chunk)
        communicate = Communicate(ssml_text, voice=voice)  # ssml=True parametresine gerek kalmadan gönder
        file_name = os.path.join(OUTPUT_DIR, f"chunk_{i+1:03}.mp3")
        await communicate.save(file_name)
        print(f"✔️  Kaydedildi: {file_name}")



def main(file_path):
    ext = pathlib.Path(file_path).suffix.lower()
    if ext == ".epub":
        text = extract_text_from_epub(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    else:
        print("❌ Desteklenmeyen dosya türü. Sadece .epub ve .docx kabul edilir.")
        return

    print(f"📘 Metin başarıyla okundu, parçalanıyor...")
    chunks = split_text(text, CHUNK_SIZE)
    print(f"🔊 {len(chunks)} ses parçası hazırlanıyor...")
    asyncio.run(convert_to_speech(chunks))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python3 edge_tts_converter.py dosya.epub|dosya.docx")
    else:
        main(sys.argv[1])

