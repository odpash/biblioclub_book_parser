import time
from multiprocessing import Pool
import multiprocessing
import os
import datetime
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
import urllib
import requests
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
import PyPDF2
import os
import reportlab


def stage_get_data():
    url = input('Введите ссылку (должна оканчиваться на "p="): ')
    book = url.split('&')
    for i in book:
        if 'b=' in i:
            book = i[2::]
            break
    pages_count = int(input('Сколько страниц в книге: '))
    pools_count = int(input('Сколько процессов использовать: (не более 60): '))
    book_name = input('Как называется книга? ')
    data = []
    c = 1
    if os.path.exists('book_' + book):
        while True:
            c += 1
            if os.path.exists('book_' + book + '_' + str(c)):
                continue
            else:
                os.mkdir('book_' + book + '_' + str(c))
                dir_link = 'book_' + book + '_' + str(c)
                break
    else:
        os.mkdir('book_' + book)
        dir_link = 'book_' + book
    os.mkdir(dir_link + '/svgs')
    os.mkdir(dir_link + '/pdfs')
    for i in range(1, pages_count + 1):
        url_link = url + str(i)
        page_name = 'page_' + str(i) + '.svg'
        data.append({'pools': pools_count, 'url': url_link, 'page_name': page_name, 'book': book, 'dir_link': dir_link,
                     'book_name': book_name,
                     'dir_svg': dir_link + '/svgs/' + page_name,
                     'dir_pdf': dir_link + '/pdfs/' + page_name.replace('svg', 'pdf')})
    return data


def stage_start_multiproccessing(data):
    pool_count = data[0]['pools']
    with Pool(pool_count) as p:
        try:
            p.map(get_and_write_data, data)
        except Exception:
            pass
    p.close()


def save_to_solo_pdf(data):
    merger = PyPDF2.PdfFileMerger()
    directory = os.path.dirname(os.path.abspath(__file__)) + '\ '.replace(' ', '') + data[0]['dir_link'] + '\pdfs'
    dir_save = os.path.dirname(os.path.abspath(__file__)) + '\ '.replace(' ', '') + data[0]['dir_link']
    for d in data:
        try:
            file_name = d['page_name'].replace('svg', 'pdf')
            merger.append(fileobj=open(os.path.join(directory, file_name), 'rb'))
        except Exception:
            pass
    merger.write(open(os.path.join(dir_save, data[0]['book_name'] + '.pdf'), 'wb'))
    print('Книга сохранена. Путь:', directory.replace('\pdfs', ' \ '.strip()) + data[0]['book_name'] + '.pdf')


def get_and_write_data(info, *count):
    try:
        img = urllib.request.urlopen(info['url']).read()
        out = open(info['dir_svg'], "wb")
        out.write(img)
        out.close
        drawing = svg2rlg(info['dir_svg'])
        renderPDF.drawToFile(drawing, info['dir_pdf'])
    except Exception:
        if count:
            if count != 5:
                time.sleep(5)
                get_and_write_data(info, count + 1)
        else:
            get_and_write_data(info, 1)


# https://viewer.biblioclub.ru/server.php?s=9rpv5dth8cgf0mfhh4lf845fo4&action=get_page&b=573147&p=  340

if __name__ == '__main__':
    multiprocessing.freeze_support()
    data = stage_get_data()
    stage_start_multiproccessing(data)
    save_to_solo_pdf(data)
    print('Программа завершила работу.')

