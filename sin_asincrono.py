from bs4 import BeautifulSoup  # Para poder usar BeautifulSoup
from urllib.parse import urlparse  # Para poder usar urlparse
import requests  # Para poder usar requests
import sys  # Para poder usar stderr
import time  # Para poder usar time


def get_images_src_from_html(html_doc): # Función para obtener las imágenes de una página
    soup = BeautifulSoup(html_doc, "html.parser") # Creamos un objeto BeautifulSoup
    return (img.get('src') for img in soup.find_all('img')) # Devolvemos la URI de la imagen


def get_uri_from_images_src(base_uri, images_src): # Función para obtener las URIs de las imágenes
    parsed_base = urlparse(base_uri) # Obtenemos la URI base
    for src in images_src: # Recorremos todas las imágenes
        parsed = urlparse(src) # Obtenemos la URI de la imagen
        if parsed.netloc == '': # Si no hay un dominio
            path = parsed.path # Obtenemos la ruta
            if parsed.query: # Si hay una consulta
                path += '?' + parsed.query # Añadimos la consulta a la ruta
            if path[0] != '/': # Si la ruta no empieza por /
                if parsed_base.path == '/': # Si la ruta base es /
                    path = '/' + path # Añadimos la ruta a la ruta base
                else: # Si no
                    path = '/' + '/'.join(parsed_base.path.split('/')
                                          [:-1]) + '/' + path
            yield parsed_base.scheme + '://' + parsed_base.netloc + path # Devolvemos la URI
        else: # Si hay un dominio
            yield parsed.geturl() # Devolvemos la URI


def get_images(page_uri): # Función para obtener las imágenes de una página
    html = wget(page_uri) # Obtenemos el contenido de la página
    if not html: # Si no hay contenido
        print("Error: no se ha encontrado ninguna imagen", sys.stderr) # Mostramos un mensaje de error
        return None # Devolvemos None
    images_src_gen = get_images_src_from_html(html) # Obtenemos las imágenes de la página
    images_uri_gen = get_uri_from_images_src(page_uri, images_src_gen) # Obtenemos las URIs de las imágenes
    for image_uri in images_uri_gen: # Recorremos todas las URIs de las imágenes
        print('Descarga de %s' % image_uri) # Mostramos un mensaje
        download(image_uri) # Descargamos la imagen


def wget(uri): # Función para obtener el contenido de una URI
    response = requests.get(uri) # Obtenemos la respuesta
    if response.status_code != 200: # Si el código de estado no es 200
        return None # Devolvemos None
    if response.headers['Content-Type'].startswith("text/"): # Si el tipo de contenido es texto
        return response.text # Devolvemos el contenido
    else: # Si no es texto
        return response.content # Devolvemos el contenido


def download(uri): # Función para descargar un fichero de una URI
    response = requests.get(uri) # Obtenemos la respuesta
    if response.status_code != 200: # Si el código de estado no es 200
        return None # Devolvemos None
    if response.headers['Content-Type'].startswith("text/"): # Si el tipo de contenido es texto
        return None # Devolvemos None
    else: # Si no es texto
        filename = uri.split('/')[-1] # Obtenemos el nombre del fichero
        with open(filename, 'wb') as f: # Abrimos el fichero
            f.write(response.content) # Escribimos el contenido


if __name__ == '__main__': # Si el script se ejecuta directamente
    start_time = time.time() # Obtenemos el tiempo de inicio
    get_images('http://www.jardinesrinconcillo.com') # Obtenemos las imágenes de la página
    print("El tiempo de ejecución sin asíncrono es de--- %s seconds ---" % (time.time() - start_time)) # Mostramos el tiempo de ejecución
