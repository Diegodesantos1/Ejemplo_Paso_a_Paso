<h1 align = "center">Ejemplo paso a paso: descarga de imágenes en asíncrono</h1>

En este [repositorio](https://github.com/Diegodesantos1/Ejemplo_Paso_a_Paso) queda resuelto el ejercicio de descarga de imágenes en asíncrono.


<h2 align = "center">Código para resolverlo</h2>

***

El código empleado para resolverlo es el siguiente:

```python
# Importamos las librerías necesarias
from urllib.parse import urlparse # Para poder usar urlparse
from bs4 import BeautifulSoup # Para poder usar BeautifulSoup
import aiohttp # Para poder usar aiohttp
import asyncio # Para poder usar asyncio
import sys # Para poder usar stderr
import functools # Para poder usar partial

async def wget(session, uri): # Función para hacer una petición GET
    async with session.get(uri) as response: # Hacemos una petición GET
        if response.status != 200: # Si el código de estado no es 200
            return None # Devolvemos None (no hay contenido)
        if response.content_type.startswith("text/"): # Si el tipo de contenido es texto
            return await response.text() # Devolvemos el contenido en texto
        else: # Si no es texto
            return await response.read() # Esperamos a que se lea el contenido

async def download(session, uri): # Función para descargar un archivo
    content = await wget(session, uri) # Hacemos una petición GET
    if content is None: # Si no hay contenido
        return None # Devolvemos None
    sep = '/' if '/' in uri else '\\' # Establecemos el separador
    with open(uri.split(sep)[-1], "wb") as f: # Abrimos el archivo
        f.write(content) # Escribimos el contenido
        return uri # Devolvemos la URI

async def get_images_src_from_html(html_doc): # Función para obtener las imágenes de una página
    soup = BeautifulSoup(html_doc, "html.parser") # Creamos un objeto BeautifulSoup
    for img in soup.find_all('img'): # Recorremos todas las imágenes
        yield img.get('src') # Devolvemos la URI de la imagen
        await asyncio.sleep(0.001) # Esperamos 1 milisegundo

async def get_uri_from_images_src(base_uri, images_src): # Función para obtener las URIs de las imágenes
    parsed_base = urlparse(base_uri) # Obtenemos la URI base
    async for src in images_src: # Recorremos todas las imágenes
        parsed = urlparse(src) # Obtenemos la URI de la imagen
        if parsed.netloc == '': # Si no hay un dominio
            path = parsed.path # Obtenemos la ruta
            if parsed.query: # Si hay una consulta
                path += '?' + parsed.query # Añadimos la consulta a la ruta
            if path[0] != '/': # Si la ruta no empieza por /
                if parsed_base.path == '/': # Si la ruta base es /
                    path = '/' + path # Añadimos la ruta a la ruta base
                else: # Si no
                    path = '/' + '/'.join(parsed_base.path.split('/')[:-1]) + '/' + path # Añadimos la ruta a la ruta base
            yield parsed_base.scheme + '://' + parsed_base.netloc + path # Devolvemos la URI
        else: # Si hay un dominio
            yield parsed.geturl() # Devolvemos la URI
        await asyncio.sleep(0.001) # Esperamos 1 milisegundo

async def get_images(session, page_uri): # Función para obtener las imágenes de una página
    html = await wget(session, page_uri) # Hacemos una petición GET
    if not html: # Si no hay contenido
        print("Error: no se ha encontrado ninguna imagen", sys.stderr) # Mostramos un mensaje de error
        return None
    images_src_gen = get_images_src_from_html(html) # Obtenemos las imágenes
    images_uri_gen = get_uri_from_images_src(page_uri, images_src_gen) # Obtenemos las URIs de las imágenes
    async for image_uri in images_uri_gen: # Recorremos todas las URIs de las imágenes
        print('Descarga de %s' % image_uri) # Mostramos un mensaje
        await download(session, image_uri) # Descargamos la imagen


async def main(): # Función principal
    web_page_uri = 'https://jardinesrinconcillo.com/' # Establecemos la URI de la página
    async with aiohttp.ClientSession() as session: # Creamos una sesión
        await get_images(session, web_page_uri) # Obtenemos las imágenes

def write_in_file(filename, content): # Función para escribir en un archivo
    with open(filename, "wb") as f: # Abrimos el archivo
        f.write(content) # Escribimos el contenido

if __name__ == "__main__": # Si es el archivo principal
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy()) # Establecemos el bucle de eventos
    asyncio.run(main()) # Ejecutamos la función principal
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
