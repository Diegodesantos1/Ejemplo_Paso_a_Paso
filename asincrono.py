# Importamos las librerías necesarias
from urllib.parse import urlparse  # Para poder usar urlparse
from bs4 import BeautifulSoup  # Para poder usar BeautifulSoup
import aiohttp  # Para poder usar aiohttp
import asyncio  # Para poder usar asyncio
import sys  # Para poder usar stderr
import functools  # Para poder usar partial
import time  # Para calcular el tiempo de ejecución


async def wget(session, uri):  # Función para hacer una petición GET
    async with session.get(uri) as response:  # Hacemos una petición GET
        if response.status != 200:  # Si el código de estado no es 200
            return None  # Devolvemos None (no hay contenido)
        # Si el tipo de contenido es texto
        if response.content_type.startswith("text/"):
            return await response.text()  # Devolvemos el contenido en texto
        else:  # Si no es texto
            return await response.read()  # Esperamos a que se lea el contenido


async def download(session, uri):  # Función para descargar un archivo
    content = await wget(session, uri)  # Hacemos una petición GET
    if content is None:  # Si no hay contenido
        return None  # Devolvemos None
    sep = '/' if '/' in uri else '\\'  # Establecemos el separador
    with open(uri.split(sep)[-1], "wb") as f:  # Abrimos el archivo
        f.write(content)  # Escribimos el contenido
        return uri  # Devolvemos la URI


# Función para obtener las imágenes de una página
async def get_images_src_from_html(html_doc):
    # Creamos un objeto BeautifulSoup
    soup = BeautifulSoup(html_doc, "html.parser")
    for img in soup.find_all('img'):  # Recorremos todas las imágenes
        yield img.get('src')  # Devolvemos la URI de la imagen
        await asyncio.sleep(0.001)  # Esperamos 1 milisegundo


# Función para obtener las URIs de las imágenes
async def get_uri_from_images_src(base_uri, images_src):
    parsed_base = urlparse(base_uri)  # Obtenemos la URI base
    async for src in images_src:  # Recorremos todas las imágenes
        parsed = urlparse(src)  # Obtenemos la URI de la imagen
        if parsed.netloc == '':  # Si no hay un dominio
            path = parsed.path  # Obtenemos la ruta
            if parsed.query:  # Si hay una consulta
                path += '?' + parsed.query  # Añadimos la consulta a la ruta
            if path[0] != '/':  # Si la ruta no empieza por /
                if parsed_base.path == '/':  # Si la ruta base es /
                    path = '/' + path  # Añadimos la ruta a la ruta base
                else:  # Si no
                    # Añadimos la ruta a la ruta base
                    path = '/' + \
                        '/'.join(parsed_base.path.split('/')[:-1]) + '/' + path
            yield parsed_base.scheme + '://' + parsed_base.netloc + path  # Devolvemos la URI
        else:  # Si hay un dominio
            yield parsed.geturl()  # Devolvemos la URI
        await asyncio.sleep(0.001)  # Esperamos 1 milisegundo


# Función para obtener las imágenes de una página
async def get_images(session, page_uri):
    html = await wget(session, page_uri)  # Hacemos una petición GET
    if not html:  # Si no hay contenido
        print("Error: no se ha encontrado ninguna imagen",
              sys.stderr)  # Mostramos un mensaje de error
        return None
    images_src_gen = get_images_src_from_html(html)  # Obtenemos las imágenes
    images_uri_gen = get_uri_from_images_src(
        page_uri, images_src_gen)  # Obtenemos las URIs de las imágenes
    async for image_uri in images_uri_gen:  # Recorremos todas las URIs de las imágenes
        print('Descarga de %s' % image_uri)  # Mostramos un mensaje
        await download(session, image_uri)  # Descargamos la imagen


async def main():  # Función principal
    # Establecemos la URI de la página
    web_page_uri = 'https://jardinesrinconcillo.com/'
    async with aiohttp.ClientSession() as session:  # Creamos una sesión
        await get_images(session, web_page_uri)  # Obtenemos las imágenes


def write_in_file(filename, content):  # Función para escribir en un archivo
    with open(filename, "wb") as f:  # Abrimos el archivo
        f.write(content)  # Escribimos el contenido


if __name__ == "__main__":  # Si es el archivo principal
    start_time = time.time()  # Establecemos el tiempo de inicio
    # Establecemos el bucle de eventos
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())  # Ejecutamos la función principal
    print("El tiempo de ejecución asíncrono es de--- %s seconds ---" %
          (time.time() - start_time))  # Mostramos el tiempo que ha tardado
