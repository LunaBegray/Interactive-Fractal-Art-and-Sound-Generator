import tkinter as tk
from tkinter import colorchooser
from cmath import exp, pi
from random import randint, random
from winsound import PlaySound
import numpy as np
from PIL import Image, ImageTk
import simpleaudio as sa  # Library for playing raw audio

def Ψ(c, λ, iterations):  # Fractal transformation
    z, v = c, []
    for _ in range(iterations):
        try:
            z = z ** λ - (c * (1j ** randint(1, 3)) * random()) / ((1 + abs(c)) ** 0.5)
            if abs(z) > 10**6:
                z /= abs(z)
            v.append(z)
        except OverflowError:
            break
    return v

def 𝛀(v, σ):  # Coordinate distortion
    return [(z.real + σ * (random() - 0.5), z.imag + σ * (random() - 0.5)) for z in v]

def χ(fractal_points, size):  # Render matrix
    grid = np.zeros(size)
    for x, y in fractal_points:
        X = int(size[0] / 2 + x * size[0] / 4) % size[0]
        Y = int(size[1] / 2 + y * size[1] / 4) % size[1]
        grid[X, Y] += 1
    return np.log(grid + 1)

def fractal_art(seed_count=25, max_iters=500, size=(500, 500)):
    seed_count = min(seed_count, 100)
    max_iters = min(max_iters, 2000)
    seeds = [(random() * 2 - 1) + (random() * 2 - 1) * 1j for _ in range(seed_count)]
    magic = lambda: random() * 2 + 1
    render = []
    for seed in seeds:
        raw = Ψ(seed, magic(), max_iters)
        render += 𝛀(raw, 0.01)
    return χ(render, size)
import numpy as np
import simpleaudio as sa

def generate_sound_from_fractal(fractal_data):
    """Generate a melodic sound based on the fractal data with harmonies."""
    height, width = fractal_data.shape
    duration = 3.0  # 1 second
    sample_rate = 44100  # 44.1 kHz audio
    base_freq = 220  # Base frequency in Hz (A3 note)
    
    # Normalize fractal values to the range 0-1
    normalized_data = fractal_data / fractal_data.max()

    # Create a time array for the audio signal
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)

    # Initialize an empty array for the audio signal
    audio_signal = np.zeros_like(t)

    # Use a harmonic progression to create a more musical effect
    for i in range(height):
        # Create a base frequency from the fractal data (scaled to a musical scale)
        freq = base_freq + normalized_data[i].mean() * 880  # Adjust scale range for melody

        # Generate a sine wave for the base frequency
        sine_wave = np.sin(2 * np.pi * freq * t)

        # Generate harmonics based on the base frequency for richness
        for harmonic in [2, 3, 4]:  # Add 2nd, 3rd, and 4th harmonics
            sine_wave += np.sin(2 * np.pi * harmonic * freq * t) / harmonic

        # Modulate amplitude with the fractal data for a dynamic, evolving sound
        amplitude = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)  # Add slow amplitude modulation (vibrato)
        sine_wave *= amplitude

        # Add the harmonic sine wave to the audio signal
        audio_signal += sine_wave

    # Normalize audio signal to fit in the 16-bit range
    audio_signal = (audio_signal / np.max(np.abs(audio_signal)) * 32767).astype(np.int16)

    # Play the sound
    play_obj = sa.play_buffer(audio_signal, 1, 2, sample_rate)
    play_obj.wait_done()


class FractalApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Interactive Fractal Art with Sound")
        self.width, self.height = 800, 800

        # Default parameters
        self.seed_count = 25
        self.iterations = 500
        self.fractal_data = None
        self.zoom_level = 1.0
        self.pan_offset = (0, 0)
        self.color_scheme = 'viridis'

        # Canvas for rendering fractals
        self.canvas = tk.Canvas(self.master, width=self.width, height=self.height)
        self.canvas.pack(side=tk.LEFT)

        # Control panel
        control_frame = tk.Frame(self.master)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Iterations slider
        tk.Label(control_frame, text="Iterations:").pack()
        self.iter_slider = tk.Scale(control_frame, from_=100, to=1000, orient=tk.HORIZONTAL)
        self.iter_slider.set(self.iterations)
        self.iter_slider.pack()

        # Seed count slider
        tk.Label(control_frame, text="Seed Count:").pack()
        self.seed_slider = tk.Scale(control_frame, from_=1, to=100, orient=tk.HORIZONTAL)
        self.seed_slider.set(self.seed_count)
        self.seed_slider.pack()

        # Zoom slider
        tk.Label(control_frame, text="Zoom:").pack()
        self.zoom_slider = tk.Scale(control_frame, from_=1, to=10, orient=tk.HORIZONTAL)
        self.zoom_slider.set(self.zoom_level)
        self.zoom_slider.pack()

        # Pan buttons
        pan_frame = tk.Frame(control_frame)
        pan_frame.pack()
        self.pan_up_button = tk.Button(pan_frame, text="Up", command=self.pan_up)
        self.pan_up_button.grid(row=0, column=1)
        self.pan_left_button = tk.Button(pan_frame, text="Left", command=self.pan_left)
        self.pan_left_button.grid(row=1, column=0)
        self.pan_right_button = tk.Button(pan_frame, text="Right", command=self.pan_right)
        self.pan_right_button.grid(row=1, column=2)
        self.pan_down_button = tk.Button(pan_frame, text="Down", command=self.pan_down)
        self.pan_down_button.grid(row=2, column=1)

        # Render button
        self.render_button = tk.Button(control_frame, text="Render Fractal", command=self.render_fractal)
        self.render_button.pack()

        # Play sound button
        self.sound_button = tk.Button(control_frame, text="Play Sound", command=self.play_sound)
        self.sound_button.pack()

        # Quit button
        self.quit_button = tk.Button(control_frame, text="Quit", command=self.master.quit)
        self.quit_button.pack()

        # Initial render
        self.render_fractal()

    def pan_up(self):
        self.pan_offset = (self.pan_offset[0], self.pan_offset[1] - 0.1)
        self.render_fractal()

    def pan_down(self):
        self.pan_offset = (self.pan_offset[0], self.pan_offset[1] + 0.1)
        self.render_fractal()

    def pan_left(self):
        self.pan_offset = (self.pan_offset[0] - 0.1, self.pan_offset[1])
        self.render_fractal()

    def pan_right(self):
        self.pan_offset = (self.pan_offset[0] + 0.1, self.pan_offset[1])
        self.render_fractal()

    def render_fractal(self):
        self.iterations = self.iter_slider.get()
        self.seed_count = self.seed_slider.get()
        self.zoom_level = self.zoom_slider.get()

        # Apply zoom and pan
        self.fractal_data = fractal_art(self.seed_count, self.iterations, size=(self.width, self.height))
        fractal_img = Image.fromarray((255 * self.fractal_data / self.fractal_data.max()).astype(np.uint8))
        fractal_img = fractal_img.convert("RGB")

        # Zoom and pan the fractal
        fractal_img = fractal_img.resize(
            (int(self.width * self.zoom_level), int(self.height * self.zoom_level)),
            Image.Resampling.NEAREST
        )
        self.img_tk = ImageTk.PhotoImage(fractal_img)

        # Update the canvas
        self.canvas.create_image(self.pan_offset[0], self.pan_offset[1], anchor=tk.NW, image=self.img_tk)

    def play_sound(self):
        if self.fractal_data is not None:
            sound = generate_sound_from_fractal(self.fractal_data)
            PlaySound(sound)

if __name__ == "__main__":
    root = tk.Tk()
    app = FractalApp(root)
    root.mainloop()
