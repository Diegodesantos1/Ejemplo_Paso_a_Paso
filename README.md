<h1 align = "center">Ejemplo paso a paso: descarga de imágenes en asíncrono</h1>

En este [repositorio](https://github.com/Diegodesantos1/Ejemplo_Paso_a_Paso) queda resuelto el ejercicio de descarga de imágenes en asíncrono.


<h2 align = "center">Código</h2>

***

El código empleado para resolverlo en asíncrono es el siguiente:

```python
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
```

El código empleado para resolverlo sin asincronía es el siguiente:

```python
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

```

<h2 align = "center">Ejemplo contrastando asincronía y no asincronía</h2>

***

En este caso he utilizado la siguiente [URL](http://jardinesrinconcillo.com/)

![image](https://user-images.githubusercontent.com/91721855/222587430-14efad6a-466f-446f-a1c8-a157ae7b412e.png)


Con lo que se han descargado de la web las siguientes imágenes:

![Gif](https://github.com/Diegodesantos1/Ejemplo_Paso_a_Paso/blob/main/loading.gif)

![Logo2](https://github.com/Diegodesantos1/Ejemplo_Paso_a_Paso/blob/main/logo_arbol_verde_v2.png)

![Plano](https://github.com/Diegodesantos1/Ejemplo_Paso_a_Paso/blob/main/plano.png)

![Logo](https://github.com/Diegodesantos1/Ejemplo_Paso_a_Paso/blob/main/logo.png)

El tiempo de ejecución en asíncrono ha sido:

![image](https://user-images.githubusercontent.com/91721855/222745909-ccb69643-fd87-4a7d-8f42-0ee9130f2d46.png)

El tiempo de ejecución sin asincronía ha sido:

![image](https://user-images.githubusercontent.com/91721855/222744835-403d7f6e-02e7-4e14-9d39-479b649f2fcd.png)

Conclusiones: el tiempo de ejecución en asíncrono es más rápido que sin usar la asincronía.
