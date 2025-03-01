import os
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk
from PIL import Image, ImageTk
import pygame
import time
import threading
from pathlib import Path

# Initialize pygame mixer
pygame.mixer.init()

# Set appearance mode and default color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MusicPlayer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Python Music Player")
        self.geometry("400x600")
        self.minsize(350, 550)
        
        # Initialize variables
        self.current_song = None
        self.songs_list = []
        self.is_playing = False
        self.is_paused = False
        self.current_song_index = 0
        self.current_time = 0
        self.song_length = 0
        
        # Create UI
        self.create_ui()
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_progress, daemon=True)
        self.update_thread.start()
    
    def create_ui(self):
        # Main frame
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top section with visualization
        self.top_frame = ctk.CTkFrame(self.main_frame, fg_color="#051a30", height=250)
        self.top_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        
        # Create a canvas for the visualization dots
        self.canvas = ctk.CTkCanvas(self.top_frame, bg="#051a30", highlightthickness=0, height=150)
        self.canvas.pack(fill=tk.X, padx=10, pady=10)
        
        # Draw the visualization dots
        self.draw_visualization_dots()
        
        # Music note image
        self.note_frame = ctk.CTkFrame(self.top_frame, fg_color="#051a30")
        self.note_frame.pack(pady=10)
        
        # Load and display music note image
        self.load_music_note_image()
        
        # Song info section
        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.info_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Song title
        self.song_title = ctk.CTkLabel(
            self.info_frame, 
            text="No song selected", 
            font=("Helvetica", 16, "bold"),
            text_color="#ffffff"
        )
        self.song_title.pack(pady=(0, 5))
        
        # Time display
        self.time_frame = ctk.CTkFrame(self.info_frame, fg_color="transparent")
        self.time_frame.pack(fill=tk.X, pady=5)
        
        self.current_time_label = ctk.CTkLabel(
            self.time_frame, 
            text="0:00", 
            font=("Helvetica", 12),
            text_color="#aaaaaa"
        )
        self.current_time_label.pack(side=tk.LEFT)
        
        self.total_time_label = ctk.CTkLabel(
            self.time_frame, 
            text="0:00", 
            font=("Helvetica", 12),
            text_color="#aaaaaa"
        )
        self.total_time_label.pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.info_frame)
        self.progress_bar.set(0)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Controls section
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Control buttons
        self.prev_button = ctk.CTkButton(
            self.controls_frame,
            text="⏮",
            font=("Helvetica", 20),
            width=60,
            height=60,
            fg_color="#0a2e52",
            hover_color="#1e4976",
            command=self.play_previous
        )
        self.prev_button.pack(side=tk.LEFT, padx=10)
        
        self.play_pause_button = ctk.CTkButton(
            self.controls_frame,
            text="▶",
            font=("Helvetica", 20),
            width=80,
            height=60,
            fg_color="#0a2e52",
            hover_color="#1e4976",
            command=self.toggle_play_pause
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=10)
        
        self.next_button = ctk.CTkButton(
            self.controls_frame,
            text="⏭",
            font=("Helvetica", 20),
            width=60,
            height=60,
            fg_color="#0a2e52",
            hover_color="#1e4976",
            command=self.play_next
        )
        self.next_button.pack(side=tk.LEFT, padx=10)
        
        # Bottom navigation tabs
        self.tabs_frame = ctk.CTkFrame(self.main_frame, fg_color="#0a2e52", height=60)
        self.tabs_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Tab buttons
        tab_width = 80
        
        self.files_tab = self.create_tab_button("Files", 0, tab_width)
        self.favorites_tab = self.create_tab_button("Favorites", 1, tab_width)
        self.music_tab = self.create_tab_button("Music", 2, tab_width, is_active=True)
        self.downloads_tab = self.create_tab_button("Downloads", 3, tab_width)
        self.status_tab = self.create_tab_button("Status", 4, tab_width)
        
        # Songs list section
        self.songs_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.songs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add songs button
        self.add_songs_button = ctk.CTkButton(
            self.songs_frame,
            text="Add Songs",
            command=self.add_songs
        )
        self.add_songs_button.pack(pady=10)
    
    def create_tab_button(self, text, position, width, is_active=False):
        tab = ctk.CTkButton(
            self.tabs_frame,
            text=text,
            font=("Helvetica", 12),
            width=width,
            height=60,
            fg_color="#0a2e52" if not is_active else "#1e4976",
            hover_color="#1e4976",
            corner_radius=0,
            command=lambda t=text: self.switch_tab(t, position)
        )
        tab.place(x=position*width, y=0)
        return tab
    
    def switch_tab(self, tab_name, position):
        # Reset all tabs
        for tab, pos in zip(
            [self.files_tab, self.favorites_tab, self.music_tab, self.downloads_tab, self.status_tab],
            range(5)
        ):
            tab.configure(fg_color="#0a2e52")
        
        # Highlight selected tab
        [self.files_tab, self.favorites_tab, self.music_tab, self.downloads_tab, self.status_tab][position].configure(
            fg_color="#1e4976"
        )
        
        print(f"Switched to {tab_name} tab")
    
    def load_music_note_image(self):
        # Create a blue music note using a label with a large font
        self.note_label = ctk.CTkLabel(
            self.note_frame,
            text="♫",
            font=("Arial", 80),
            text_color="#0a84ff",
            width=100,
            height=100
        )
        self.note_label.pack()
    
    def draw_visualization_dots(self):
        # Clear canvas
        self.canvas.delete("all")
        
        # Draw grid of dots
        rows, cols = 8, 20
        dot_size = 4
        spacing = 15
        
        for i in range(rows):
            for j in range(cols):
                # Calculate position
                x = j * spacing + 20
                y = i * spacing + 20
                
                # Determine opacity based on position (creating a circular pattern)
                center_x, center_y = cols * spacing / 2, rows * spacing / 2
                distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                max_distance = ((center_x) ** 2 + (center_y) ** 2) ** 0.5
                opacity = max(0, min(255, int(255 * (1 - distance / max_distance))))
                
                # Add some randomness to make it look more dynamic
                import random
                if self.is_playing:
                    opacity = max(0, min(255, opacity + random.randint(-50, 50)))
                
                # Convert to hex
                hex_opacity = format(opacity, '02x')
                color = f"#0a84ff{hex_opacity}"
                
                # Draw dot
                self.canvas.create_oval(
                    x - dot_size, y - dot_size,
                    x + dot_size, y + dot_size,
                    fill=color, outline=""
                )
        
        # Schedule next update if playing
        if self.is_playing and not self.is_paused:
            self.after(100, self.draw_visualization_dots)
    
    def add_songs(self):
        # Open file dialog to select music files
        file_paths = filedialog.askopenfilenames(
            title="Select Music Files",
            filetypes=[("Audio Files", "*.mp3 *.wav *.ogg")]
        )
        
        if file_paths:
            for path in file_paths:
                # Get song name from file path
                song_name = os.path.basename(path)
                
                # Create a frame for the song
                song_frame = ctk.CTkFrame(self.songs_frame, fg_color="transparent")
                song_frame.pack(fill=tk.X, pady=5)
                
                # Add song button
                song_button = ctk.CTkButton(
                    song_frame,
                    text=song_name,
                    anchor="w",
                    fg_color="#0a2e52",
                    hover_color="#1e4976",
                    command=lambda p=path, n=song_name: self.play_song(p, n)
                )
                song_button.pack(fill=tk.X)
                
                # Add to songs list
                self.songs_list.append({"path": path, "name": song_name, "button": song_button})
            
            # If this is the first song added, select it
            if len(self.songs_list) == 1:
                self.current_song = self.songs_list[0]["path"]
                self.current_song_index = 0
                self.song_title.configure(text=self.songs_list[0]["name"])
    
    def play_song(self, path, name):
        # Stop current song if playing
        pygame.mixer.music.stop()
        
        # Load and play the new song
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        
        # Update UI
        self.current_song = path
        self.current_song_index = next((i for i, song in enumerate(self.songs_list) if song["path"] == path), 0)
        self.song_title.configure(text=name)
        self.is_playing = True
        self.is_paused = False
        self.play_pause_button.configure(text="⏸")
        
        # Get song length
        self.song_length = pygame.mixer.Sound(path).get_length()
        mins, secs = divmod(int(self.song_length), 60)
        self.total_time_label.configure(text=f"{mins}:{secs:02d}")
        
        # Reset progress
        self.current_time = 0
        self.progress_bar.set(0)
        
        # Update visualization
        self.draw_visualization_dots()
        
        # Highlight current song
        for song in self.songs_list:
            if song["path"] == path:
                song["button"].configure(fg_color="#1e4976")
            else:
                song["button"].configure(fg_color="#0a2e52")
    
    def toggle_play_pause(self):
        if not self.current_song:
            return
        
        if self.is_paused:
            # Resume playback
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.play_pause_button.configure(text="⏸")
            self.draw_visualization_dots()
        else:
            if self.is_playing:
                # Pause playback
                pygame.mixer.music.pause()
                self.is_paused = True
                self.play_pause_button.configure(text="▶")
            else:
                # Start playback
                self.play_song(self.current_song, self.songs_list[self.current_song_index]["name"])
    
    def play_next(self):
        if not self.songs_list:
            return
        
        # Get next song index
        next_index = (self.current_song_index + 1) % len(self.songs_list)
        next_song = self.songs_list[next_index]
        
        # Play the next song
        self.play_song(next_song["path"], next_song["name"])
    
    def play_previous(self):
        if not self.songs_list:
            return
        
        # Get previous song index
        prev_index = (self.current_song_index - 1) % len(self.songs_list)
        prev_song = self.songs_list[prev_index]
        
        # Play the previous song
        self.play_song(prev_song["path"], prev_song["name"])
    
    def update_progress(self):
        while True:
            if self.is_playing and not self.is_paused and self.song_length > 0:
                # Get current position
                try:
                    self.current_time = pygame.mixer.music.get_pos() / 1000
                    
                    # Update progress bar
                    progress = self.current_time / self.song_length
                    self.progress_bar.set(progress)
                    
                    # Update time label
                    mins, secs = divmod(int(self.current_time), 60)
                    self.current_time_label.configure(text=f"{mins}:{secs:02d}")
                    
                    # Check if song ended
                    if not pygame.mixer.music.get_busy() and not self.is_paused:
                        self.play_next()
                except:
                    pass
            
            time.sleep(0.1)

if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()
