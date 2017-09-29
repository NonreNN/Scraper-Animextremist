import argparse
import requests
import bs4
import os
import zipfile
from zipfile import ZipFile


ANIMEXTREMIST_URL = "http://animextremist.com/"

def download_chapter(link_manga):
    download_chapter = requests.get(link_manga)
    status_chapter = download_chapter.raise_for_status()
    soup_chapter = bs4.BeautifulSoup(download_chapter.content, "html5lib")
    for option in soup_chapter.find_all('select', id="nav-jump"):
        list_img = []
        index_img = 0
        print ("Descargando imagenes de", soup_chapter.title.string)
        for img_list in option.find_all("option"):
            chapter_link = ANIMEXTREMIST_URL + img_list.get('value')
            download_img = requests.get(chapter_link)
            status_download_img = download_img.raise_for_status()
            soup_img = bs4.BeautifulSoup(download_img.content, "html5lib")
            chapter_name = soup_img.title.string
            for img in soup_img.find_all('img', id="photo"):
                download_img = img.get('src')
                img_request = requests.get(download_img)
                status_img = img_request.raise_for_status()
                img_content = img_request.content
                byte_image = bytes(img_content)
                if index_img <= 9:
                    name_file = "00" + str(index_img) + download_img[-4:]
                elif index_img>= 10 and index_img <= 99:
                    name_file = "0" + str(index_img) + download_img[-4:]
                else:
                    name_file = str(index_img) + download_img[-4:]
                index_img += 1
                print ("Descargando imagen %s" % download_img)
                img_file = open(name_file, 'wb')
                img_file.write(byte_image)
                img_file.close()
                list_img.append(name_file)

        fzip = zipfile.ZipFile(chapter_name + ".cbz", "w")
        print ("Creando archivo cbz", chapter_name)
        for img_file in list_img:
            fzip.write(img_file)
            os.unlink(img_file)

def all_list_chapter(url):
    download_chapter = requests.get(url)
    status_chapter = download_chapter.raise_for_status()
    soup = bs4.BeautifulSoup(download_chapter.content, "html5lib")
    list_chapter = []
    print ("Buscando links de los capitulos...")
    for option in soup.find_all('select', id="cap-jump"):
        for img_list in option.find_all("option"):
            link_manga = ANIMEXTREMIST_URL + img_list.get('value')
            download_chapter = requests.get(link_manga)
            status_chapter = download_chapter.raise_for_status()
            soup_chapter = bs4.BeautifulSoup(download_chapter.content, "html5lib")
            for tag_class in soup_chapter.findAll('div', {'class': 'style33'}):
                for a in tag_class.find_all('a'):
                    link = a.get('href')
                    print (link)
                    list_chapter.append(link)
    return list_chapter

def make_folder(url):
    download_chapter = requests.get(url)
    status_chapter = download_chapter.raise_for_status()
    soup = bs4.BeautifulSoup(download_chapter.content, "html5lib")
    folder_name = soup.title.string.split(" - ",1)
    try:
        if os.path.isfile(folder_name[0]):
            print ("")
        else:
            os.makedirs(folder_name[0])
            print ("Creando carpeta del manga [%s]" % folder_name[0])
    except OSError as e:
        print ("Entrando en la carpeta del manga [%s]" % folder_name[0])

    os.chdir(folder_name[0])

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u",
        "--url",
        help="url del manga a descargar",
    )
    parser.add_argument(
        "-d",
        "--download",
        action="store_true",
        help="descarga un capitulo",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="descarga todos los capitulos",
    )
    args = parser.parse_args()

    make_folder(args.url)

    if args.download == True:
        download_chapter(args.url)

    elif args.all == True:
        link_chapter = all_list_chapter(args.url)
        for link in link_chapter:
            download_chapter(link)
