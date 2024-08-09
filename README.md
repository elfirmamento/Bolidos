# Bolidos
programa de detección de meteoros y bólidos en archivos MP4

Lenguaje Python v.3.10
requiere librerias como ser OpenCV hasta la versión 0.6 incluida.
Desde la versión 0.7 (aún con errores) requiere agregar las librerías torch y torchvision para utilizar el modelo YOLOv5s

El programa sigue en beta y requiere varios ajustes para una mejor detección como corrección de errores.
Se utilizan una combinación de distintos parámetros para detectar trazas, destellos, comparación de frames, entre otros.
El programa detecta eventos meteoros o bólidos, captura la imagen y la guarda en formato jpg en la carpeta llamada "eventos_detectados" 
y a su vez crea (si no existe) un archivo txt llamado "events_info.txt" para guardar el registro tanto de las coordenadas, tiempo, número de evento 

Para utilizar un video formato mp4, por el momento, lo llamo video4.mp4

Versión 0.7 /////////////
en la cual poseo problemas en el uso de librería, quiero utilizar torch y torchvision llamando el modelo YOLOv5s
para trabajar con una base de datos de autoaprendizaje; de esta manera, cuando registra un evento, lo agrega a la base teniendo así
diferentes tipos de bólidos o meteoros detectados para ser usados en la detección de futuros eventos.

Hasta el momento tira error en la línea 6 "import torch". Tengo la librería cargada y me gustaría seguir avanzando en el presente proyecto
mejorando entre todos los resultados.


