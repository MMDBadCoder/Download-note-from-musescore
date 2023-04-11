import json
import os
import pathlib
import shutil

import requests
import wget
from PyPDF2 import PdfMerger
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg


def download_images(musescore_id, base_path):
    headers = {
        'authority': 'musescore.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9,fa;q=0.8',
        'authorization': '8c022bdef45341074ce876ae57a48f64b86cdcf5',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://musescore.com/user/16368961/scores/6634640',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
    }

    for i in range(20):
        params = {
            'id': musescore_id,
            'index': str(i),
            'type': 'img',
            'v2': '1',
        }

        response = requests.get('https://musescore.com/api/jmuse', params=params, headers=headers)
        img_url = json.loads(response.content)['info']['url']
        out_path = base_path + '/' + str(i) + '.svg'
        try:
            wget.download(img_url, out=out_path)
        except Exception as e:
            break


url = input("put the url of musescore page:")
musescore_id = url.split('/')[-1]
base_path = pathlib.Path(__file__).parent.resolve()
base_path = str(base_path) + "/" + musescore_id

if os.path.exists(base_path):
    shutil.rmtree(base_path)
os.makedirs(base_path)

print('Downloading...')
download_images(musescore_id, base_path)

pdf_files = []
print('Converting...')
for path, subdirs, files in os.walk(base_path):
    for file in files:
        if file.endswith('.svg'):
            abspath_svg = path + os.sep + file
            pdf_path = abspath_svg + '.pdf'
            drawing = svg2rlg(abspath_svg)
            renderPDF.drawToFile(drawing, pdf_path)
            pdf_files.append(pdf_path)
            os.remove(abspath_svg)

pdf_files.sort()
with PdfMerger() as merger:
    for pdf in pdf_files:
        merger.append(pdf)
    merger.write(musescore_id + "-note.pdf")

shutil.rmtree(base_path)
print('Finished')
