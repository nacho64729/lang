import os
import sys
import time
import urllib.parse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import cairosvg

def setup_driver():
    options = Options()
    options.headless = True
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)
    return driver

def fetch_svgs(driver, character):
    encoded_char = urllib.parse.quote(character)
    url = f"https://www.chinesehideout.com/tools/strokeorder.php?c={encoded_char}"
    driver.get(url)
    time.sleep(1.5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    sequence_div = soup.find("div", id="sequence")
    if not sequence_div:
        return []

    return sequence_div.find_all("svg")

def save_pngs(character, svg_elements):
    os.makedirs(character, exist_ok=True)
    for idx, svg in enumerate(svg_elements, 1):
        filename = os.path.join(character, f"{idx}.png")
        svg_code = str(svg)
        try:
            # Save the PNG at 100x100
            cairosvg.svg2png(bytestring=svg_code.encode('utf-8'), write_to=filename, output_width=100, output_height=100)
            
            # Open and crop the image to top-left 85x85
            with Image.open(filename) as img:
                cropped_img = img.crop((0, 0, 85, 85))
                cropped_img.save(filename)

        except Exception as e:
            print(f"Failed to convert or crop SVG {idx} for {character}: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_strokes.py <char1> <char2> ...")
        sys.exit(1)

    chars = sys.argv[1:]
    driver = setup_driver()

    for char in chars:
        print(f"Processing: {char}")
        svg_elements = fetch_svgs(driver, char)
        if not svg_elements:
            print(f"No stroke order SVGs found for '{char}'")
        else:
            save_pngs(char, svg_elements)
            print(f"Saved {len(svg_elements)} PNGs for '{char}'")

    driver.quit()

if __name__ == "__main__":
    main()
