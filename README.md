# 🎵 Reproductor de Música con Flet y VLC

¡Bienvenido a tu propio reproductor de música moderno hecho en Python!  
Este proyecto te permite escuchar tus canciones favoritas en formatos populares como **MP3** y **M4A**, con una interfaz inspirada en Spotify.

## 🚀 Características

- Interfaz gráfica elegante y responsiva (Flet)
- Soporte para archivos `.mp3` y `.m4a` (usando VLC)
- Lista de reproducción dinámica
- Controles de reproducción: play, pausa, siguiente, anterior
- Barra de progreso y control de volumen
- Modo aleatorio y repetir
- Visualización de título y artista
- Colores y diseño inspirados en Spotify

## 🖥️ Captura de pantalla

![Captura de pantalla del reproductor](/img/screenshot.png)

## 📦 Requisitos

- Python 3.8 o superior
- [VLC Media Player](https://www.videolan.org/vlc/) instalado y en el PATH
- Las siguientes librerías de Python:
  - flet
  - python-vlc
  - mutagen

## ⚡ Instalación

1. Clona este repositorio:
   ```
   git clone https://github.com/tuusuario/reproductor-musica-flet.git
   cd reproductor-musica-flet
   ```

2. Instala las dependencias:
   ```
   pip install flet python-vlc mutagen
   ```

3. Ejecuta el programa:
   ```
   python main.py
   ```

## 🎧 Uso

- Haz clic en **Cargar Canciones** para añadir archivos de música a la lista.
- Usa los controles para reproducir, pausar, avanzar o retroceder canciones.
- Ajusta el volumen y la posición de la canción con los sliders.
- Activa el modo aleatorio o repetir según prefieras.

## 📝 Créditos

- Interfaz creada con [Flet](https://flet.dev/)
- Reproducción de audio gracias a [python-vlc](https://pypi.org/project/python-vlc/)
- Lectura de metadatos con [mutagen](https://mutagen.readthedocs.io/en/latest/)
