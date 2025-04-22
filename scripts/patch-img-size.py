from bs4 import BeautifulSoup

def modify_html(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        contents = f.read()

    soup = BeautifulSoup(contents, 'html.parser')

    for img in soup.find_all('img'):
        if img.has_attr('width'):
            img['width'] = '100%'
        if img.has_attr('height'):
            img['height'] = '100%'

    with open(filename, 'w', encoding='utf-8') as f:
        f.write(str(soup))

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 script.py filename")
        sys.exit(1)

    modify_html(sys.argv[1])