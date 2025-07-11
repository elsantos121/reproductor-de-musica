import flet as ft
import vlc
import os
import time
import threading
from pathlib import Path
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import random

class MusicPlayer:
    def __init__(self, page: ft.Page):
        self.page = page
        self.current_song = None
        self.current_index = 0
        self.playlist = []
        self.is_playing = False
        self.is_paused = False
        self.volume = 0.7
        self.duration = 0
        self.position = 0
        self.shuffle_mode = False
        self.repeat_mode = False
        self.update_thread = None
        self.stop_update = False

        # Inicializar VLC player
        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()
        self.player.audio_set_volume(int(self.volume * 100))

        # Configurar página
        self.page.title = "Reproductor de Música"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.window_width = 800
        self.page.window_height = 600
        self.page.window_resizable = True

        self.setup_ui()

    def setup_ui(self):
        # Área de información de la canción
        self.song_title = ft.Text(
            "Selecciona una canción",
            size=20,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )
        
        self.song_artist = ft.Text(
            "Artista desconocido",
            size=14,
            color=ft.Colors.GREY_500,
            text_align=ft.TextAlign.CENTER
        )
        
        self.song_info = ft.Container(
            content=ft.Column([
                self.song_title,
                self.song_artist
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            alignment=ft.alignment.center
        )
        
        # Barra de progreso
        self.progress_bar = ft.Slider(
            min=0,
            max=100,
            value=0,
            on_change=self.on_progress_change,
            thumb_color=ft.Colors.BLUE_400,
            active_color=ft.Colors.BLUE_400,
            inactive_color=ft.Colors.GREY_300
        )
        
        # Etiquetas de tiempo
        self.time_current = ft.Text("00:00", size=12)
        self.time_total = ft.Text("00:00", size=12)
        
        self.time_container = ft.Row([
            self.time_current,
            ft.Container(expand=True),
            self.time_total
        ])
        
        # Controles de reproducción
        self.play_pause_btn = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW,
            icon_size=40,
            on_click=self.toggle_play_pause
        )
        
        self.prev_btn = ft.IconButton(
            icon=ft.Icons.SKIP_PREVIOUS,
            icon_size=30,
            on_click=self.previous_song
        )
        
        self.next_btn = ft.IconButton(
            icon=ft.Icons.SKIP_NEXT,
            icon_size=30,
            on_click=self.next_song
        )
        
        self.shuffle_btn = ft.IconButton(
            icon=ft.Icons.SHUFFLE,
            icon_size=25,
            on_click=self.toggle_shuffle
        )
        
        self.repeat_btn = ft.IconButton(
            icon=ft.Icons.REPEAT,
            icon_size=25,
            on_click=self.toggle_repeat
        )
        
        # Control de volumen
        self.volume_slider = ft.Slider(
            min=0,
            max=1,
            value=self.volume,
            on_change=self.on_volume_change,
            width=150,
            thumb_color=ft.Colors.BLACK,
            active_color=ft.Colors.BLACK
        )
        
        self.volume_icon = ft.Icon(ft.Icons.VOLUME_UP)
        
        # Lista de reproducción
        self.playlist_view = ft.ListView(
            expand=True,
            spacing=5,
            padding=10
        )
        
        # Botones de acción
        self.load_btn = ft.ElevatedButton(
            "Cargar Canciones",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self.load_songs
        )

        self.clear_btn = ft.ElevatedButton(
            "Limpiar Lista",
            icon=ft.Icons.CLEAR,
            on_click=self.clear_playlist
        )
        
        # Layout principal
        controls_row = ft.Row([
            self.shuffle_btn,
            self.prev_btn,
            self.play_pause_btn,
            self.next_btn,
            self.repeat_btn
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        volume_row = ft.Row([
            self.volume_icon,
            self.volume_slider,
            ft.Text("Vol")
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        buttons_row = ft.Row([
            self.load_btn,
            self.clear_btn
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # Panel izquierdo (reproductor)
        player_panel = ft.Container(
            content=ft.Column([
                self.song_info,
                ft.Container(height=10),
                self.progress_bar,
                self.time_container,
                ft.Container(height=10),
                controls_row,
                ft.Container(height=20),
                volume_row,
                ft.Container(height=20),
                buttons_row
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            width=400,
            padding=20,
            bgcolor="#191414",  # Negro Spotify
            border_radius=10
        )

        # Panel derecho (playlist)
        playlist_panel = ft.Container(
            content=ft.Column([
                ft.Text("Lista de Reproducción", size=18, weight=ft.FontWeight.BOLD),
                ft.Container(height=10),
                self.playlist_view
            ]),
            expand=True,
            padding=20,
            bgcolor="#191414",  # Negro Spotify
            border_radius=10
        )

        # Layout principal
        main_layout = ft.Row([
            player_panel,
            ft.Container(width=20),
            playlist_panel
        ], expand=True)

        # Cambia el fondo de la página a verde Spotify
        self.page.bgcolor = "#1DB954"
        self.page.add(main_layout)
        
        # Iniciar hilo de actualización
        self.start_update_thread()
    
    def format_time(self, seconds):
        """Formatear tiempo en mm:ss"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_song_info(self, file_path):
        """Obtener información de la canción"""
        try:
            if file_path.lower().endswith('.mp3'):
                audio = MP3(file_path)
                title = audio.get('TIT2', [Path(file_path).stem])[0]
                artist = audio.get('TPE1', ['Artista desconocido'])[0]
            elif file_path.lower().endswith('.m4a'):
                audio = MP4(file_path)
                title = audio.get('\xa9nam', [Path(file_path).stem])[0]
                artist = audio.get('\xa9ART', ['Artista desconocido'])[0]
            else:
                title = Path(file_path).stem
                artist = 'Artista desconocido'
            
            return str(title), str(artist)
        except:
            return Path(file_path).stem, 'Artista desconocido'
    
    def load_songs(self, e):
        """Cargar canciones desde una carpeta"""
        def on_result(result: ft.FilePickerResultEvent):
            if result.files:
                for file in result.files:
                    if file.path.lower().endswith(('.mp3', '.m4a')):
                        self.playlist.append(file.path)
                        title, artist = self.get_song_info(file.path)
                        
                        # Crear elemento de lista
                        song_item = ft.ListTile(
                            title=ft.Text(title, size=14),
                            subtitle=ft.Text(artist, size=12, color=ft.Colors.GREY_500),
                            on_click=lambda e, idx=len(self.playlist)-1: self.play_song_at_index(idx),
                            bgcolor=ft.Colors.SURFACE,
                            shape=ft.RoundedRectangleBorder(radius=5)
                        )
                        
                        self.playlist_view.controls.append(song_item)
                
                self.page.update()
        
        file_picker = ft.FilePicker(on_result=on_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        file_picker.pick_files(
            dialog_title="Seleccionar canciones",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=['mp3', 'm4a'],
            allow_multiple=True
        )
    
    def clear_playlist(self, e):
        """Limpiar la lista de reproducción"""
        self.stop_playback()
        self.playlist.clear()
        self.playlist_view.controls.clear()
        self.current_index = 0
        self.song_title.value = "Selecciona una canción"
        self.song_artist.value = "Artista desconocido"
        self.progress_bar.value = 0
        self.time_current.value = "00:00"
        self.time_total.value = "00:00"
        self.page.update()
    
    def play_song_at_index(self, index):
        """Reproducir canción en un índice específico"""
        if 0 <= index < len(self.playlist):
            self.current_index = index
            self.play_current_song()
            self.update_playlist_ui()
    
    def play_current_song(self):
        """Reproducir la canción actual"""
        if not self.playlist:
            return

        try:
            self.stop_playback()

            song_path = self.playlist[self.current_index]
            media = self.vlc_instance.media_new(song_path)
            self.player.set_media(media)
            self.player.play()

            self.is_playing = True
            self.is_paused = False
            self.play_pause_btn.icon = ft.Icons.PAUSE

            # Actualizar información de la canción
            title, artist = self.get_song_info(song_path)
            self.song_title.value = title
            self.song_artist.value = artist

            # Obtener duración
            try:
                time.sleep(0.1)  # Espera para que VLC obtenga la duración
                self.duration = self.player.get_length() / 1000
            except:
                self.duration = 0

            self.time_total.value = self.format_time(self.duration)
            self.progress_bar.max = self.duration if self.duration > 0 else 100

            self.page.update()

        except Exception as e:
            print(f"Error al reproducir: {e}")

    def stop_playback(self):
        """Detener reproducción"""
        try:
            self.player.stop()
            self.is_playing = False
            self.is_paused = False
            self.position = 0
            self.play_pause_btn.icon = ft.Icons.PLAY_ARROW
            self.page.update()
        except:
            pass
    
    def toggle_play_pause(self, e):
        """Alternar play/pause"""
        if not self.playlist:
            return
        
        if self.is_playing:
            if self.is_paused:
                self.player.play()
                self.is_paused = False
                self.play_pause_btn.icon = ft.Icons.PAUSE
            else:
                self.player.pause()
                self.is_paused = True
                self.play_pause_btn.icon = ft.Icons.PLAY_ARROW
        else:
            self.play_current_song()
        
        self.page.update()
    
    def previous_song(self, e):
        """Canción anterior"""
        if not self.playlist:
            return
        
        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index - 1) % len(self.playlist)
        
        self.play_current_song()
        self.update_playlist_ui()
    
    def next_song(self, e):
        """Canción siguiente"""
        if not self.playlist:
            return
        
        if self.shuffle_mode:
            self.current_index = random.randint(0, len(self.playlist) - 1)
        else:
            self.current_index = (self.current_index + 1) % len(self.playlist)
        
        self.play_current_song()
        self.update_playlist_ui()
    
    def toggle_shuffle(self, e):
        """Alternar modo aleatorio"""
        self.shuffle_mode = not self.shuffle_mode
        self.shuffle_btn.icon_color = ft.Colors.BLUE_400 if self.shuffle_mode else None
        self.repeat_btn.icon_color = ft.Colors.BLUE_400 if self.repeat_mode else None
        self.page.update()
    
    def toggle_repeat(self, e):
        """Alternar modo repetir"""
        self.repeat_mode = not self.repeat_mode
        self.repeat_btn.icon_color = ft.Colors.BLUE_400 if self.repeat_mode else None
        self.page.update()
    
    def on_volume_change(self, e):
        """Cambiar volumen"""
        self.volume = self.volume_slider.value
        self.player.audio_set_volume(int(self.volume * 100))
        
        # Actualizar icono según volumen
        if self.volume == 0:
            self.volume_icon.name = ft.Icons.VOLUME_OFF
        elif self.volume < 0.5:
            self.volume_icon.name = ft.Icons.VOLUME_DOWN
        else:
            self.volume_icon.name = ft.Icons.VOLUME_UP
        
        self.page.update()
    
    def on_progress_change(self, e):
        """Cambiar posición de reproducción"""
        if self.is_playing and self.duration > 0:
            new_position = self.progress_bar.value
            self.player.set_time(int(new_position * 1000))
            self.position = new_position
            self.time_current.value = self.format_time(new_position)
            self.page.update()
    
    def update_playlist_ui(self):
        """Actualizar interfaz de playlist"""
        for i, item in enumerate(self.playlist_view.controls):
            if i == self.current_index:
                item.bgcolor = ft.Colors.BLUE_100
                item.title.color = ft.Colors.BLUE_800
            else:
                item.bgcolor = ft.Colors.SURFACE
                item.title.color = None
        self.page.update()
    
    def start_update_thread(self):
        """Iniciar hilo de actualización"""
        def update_loop():
            while not self.stop_update:
                if self.is_playing and not self.is_paused:
                    # Actualizar posición
                    self.position += 1
                    
                    # Verificar si la canción terminó
                    if not self.player.is_playing() and self.position > 1:
                        if self.repeat_mode:
                            self.play_current_song()
                        else:
                            self.next_song(None)
                    
                    # Actualizar UI
                    if self.duration > 0:
                        self.progress_bar.value = min(self.position, self.duration)
                        self.time_current.value = self.format_time(self.position)
                        self.page.update()
                
                time.sleep(1)
        
        self.update_thread = threading.Thread(target=update_loop, daemon=True)
        self.update_thread.start()

def main(page: ft.Page):
    player = MusicPlayer(page)

if __name__ == "__main__":
    ft.app(target=main)