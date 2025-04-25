
# 📚 Edge-TTS ile EPUB'tan Türkçe Sesli Kitap Oluşturma Rehberi

Bu rehber, Ubuntu sisteminde EPUB dosyalarını ücretsiz ve doğal sesle sesli kitaba çevirmenin adımlarını anlatır. Kullanılan ses motoru: **Edge-TTS (Microsoft'un çevrimdışı çalışabilen TTS API’si)**

---

## 🚀 Kurulum Adımları

### 1. Gerekli Paketleri Yükleyin
Ubuntu'da `venv` ve Python geliştirme paketlerini yükleyin:

```bash
sudo apt update
sudo apt install python3-venv python3-pip ffmpeg
```

### 2. Proje Dizini Oluşturun

```bash
mkdir ~/tts_projem
cd ~/tts_projem
python3 -m venv venv
source venv/bin/activate
```

### 3. Gerekli Kütüphaneleri Kurun

```bash
pip install -U edge-tts ebooklib python-docx
```

---

## 🛠️ Python Scripti (edge_tts_converter.py)

Ana betik dosyasını oluşturun:

```bash
nano edge_tts_converter.py
```

İçine aşağıdaki kodu yapıştırın:

```python
import os
import sys
import asyncio
from ebooklib import epub
from edge_tts import Communicate

OUTPUT_DIR = "output"

def extract_text_from_epub(file_path):
    book = epub.read_epub(file_path)
    text = ""
    for item in book.items:
        if item.get_type() == 9:  # ITEM_DOCUMENT
            content = item.get_content().decode("utf-8")
            text += content.replace("\n", " ") + "\n"
    return text

def split_text(text, max_len=3000):
    paragraphs = text.split("\n")
    chunks, current = [], ""
    for p in paragraphs:
        if len(current) + len(p) < max_len:
            current += p + "\n"
        else:
            chunks.append(current.strip())
            current = p + "\n"
    if current:
        chunks.append(current.strip())
    return chunks

def format_ssml(text):
    sentences = text.strip().split('.')
    ssml = "<speak>"
    for sentence in sentences:
        clean = sentence.strip()
        if clean:
            ssml += f"<s>{clean}.</s>"
    ssml += "</speak>"
    return ssml

async def convert_to_speech(chunks, voice="tr-TR-EmelNeural"):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for i, chunk in enumerate(chunks):
        ssml_text = format_ssml(chunk)
        communicate = Communicate(ssml_text, voice=voice)
        file_name = os.path.join(OUTPUT_DIR, f"chunk_{i+1:03}.mp3")
        await communicate.save(file_name)
        print(f"✔️  Kaydedildi: {file_name}")

def main(epub_path):
    print(f"📘 Metin işleniyor: {epub_path}")
    text = extract_text_from_epub(epub_path)
    print("📘 Metin başarıyla okundu, parçalanıyor...")
    chunks = split_text(text)
    print(f"🔊 {len(chunks)} ses parçası hazırlanıyor...")
    asyncio.run(convert_to_speech(chunks))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Kullanım: python3 edge_tts_converter.py <dosya.epub>")
    else:
        main(sys.argv[1])
```

---

## 📦 Kullanım

### EPUB dosyasını MP3’e dönüştürmek için:

```bash
python3 edge_tts_converter.py kitap.epub
```

Oluşan MP3 dosyaları `output` klasörüne kaydedilir.

---

## 🗣️ Ekstra: Farklı Türkçe Sesler

| Ses İsmi             | Açıklama           |
|----------------------|--------------------|
| `tr-TR-EmelNeural`   | Kadın sesi (varsayılan) |
| `tr-TR-AhmetNeural`  | Erkek sesi         |

Kullanmak için şu satırı değiştir:
```python
await convert_to_speech(chunks, voice="tr-TR-AhmetNeural")
```

---

## 🎧 Sonraki Adımlar

İstersen:
- MP3 dosyalarını birleştirip tek bir sesli kitap haline getirebilirsin (`ffmpeg` ile).
- DOCX dosyalarıyla çalışmak istersen, kodu çok kolayca güncelleyebiliriz.
