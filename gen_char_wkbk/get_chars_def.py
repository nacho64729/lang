import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup

def get_pnyn_def(char):
    encoded_char = urllib.parse.quote(char)
    url = f"https://www.chinesehideout.com/tools/strokeorder.php?c={encoded_char}"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Look for the <div id="mydef"> block
    header = soup.find('div', id='mydef')
    if header:
        phrase = header.get_text(strip=True).split("radical")[0] # 俩 (倆) [liă liăng] - two, a pair, a couple
        pnyn = phrase.split("[")[1].split("]")[0]
        definit = phrase.split("- ")[1]
        return pnyn, definit
    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python get_char_defs.py <char1> <char2> ...")
        sys.exit(1)

    chars = sys.argv[1:]
    char_info = {}

    for char in chars:
        print(f"Fetching: {char}")
        pinyin, definition = get_pnyn_def(char)
        if definition:
            char_info[char] = [pinyin, definition]
            print(f"{char}: [{pinyin}], [{definition}]")
        else:
            print(f"No definition found for '{char}'")

    print("\nFull dictionary:")
    print(char_info)

if __name__ == "__main__":
    main()