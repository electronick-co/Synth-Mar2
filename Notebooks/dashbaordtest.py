import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from matplotlib.figure import Figure
import random

class VibrationDashboard:
    def __init__(self, master):
        self.master = master
        master.title("Vibration Sensor Dashboard")

        # Create tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')

        # Real-time data tab
        self.real_time_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.real_time_frame, text='Real-time Data')

        # FFT tab
        self.fft_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fft_frame, text='FFT Analysis')

        # Status frame
        self.status_frame = ttk.Frame(master)
        self.status_frame.pack(pady=10)

        # Initialize plots
        self.init_real_time_plot()
        self.init_fft_plot()

        # Initialize status
        self.status_label = ttk.Label(self.status_frame, text="Status: Normal", font=("Arial", 14))
        self.status_label.pack()

        # Start updating
        self.update()

    def init_real_time_plot(self):
        self.real_time_fig = Figure(figsize=(6, 4), dpi=100)
        self.real_time_ax = self.real_time_fig.add_subplot(111)
        self.real_time_ax.set_title("Real-time Vibration Data")
        self.real_time_ax.set_xlabel("Time")
        self.real_time_ax.set_ylabel("Amplitude")
        self.real_time_lines = [self.real_time_ax.plot([], [], label=axis)[0] for axis in ['X', 'Y', 'Z']]
        self.real_time_ax.legend()

        self.real_time_canvas = FigureCanvasTkAgg(self.real_time_fig, master=self.real_time_frame)
        self.real_time_canvas.draw()
        self.real_time_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.real_time_data = [[], [], []]

    def init_fft_plot(self):
        self.fft_fig = Figure(figsize=(6, 4), dpi=100)
        self.fft_ax = self.fft_fig.add_subplot(111)
        self.fft_ax.set_title("FFT Analysis")
        self.fft_ax.set_xlabel("Frequency (Hz)")
        self.fft_ax.set_ylabel("Amplitude")

        self.fft_canvas = FigureCanvasTkAgg(self.fft_fig, master=self.fft_frame)
        self.fft_canvas.draw()
        self.fft_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    def update(self):
        # Update real-time data
        for i in range(3):
            self.real_time_data[i].append(random.uniform(0, 10))
            if len(self.real_time_data[i]) > 50:
                self.real_time_data[i].pop(0)
            self.real_time_lines[i].set_data(range(len(self.real_time_data[i])), self.real_time_data[i])

        self.real_time_ax.relim()
        self.real_time_ax.autoscale_view()
        self.real_time_canvas.draw()

        # Update FFT plot
        fft_data = np.fft.fft(self.real_time_data[0])
        freqs = np.fft.fftfreq(len(fft_data), 0.1)
        self.fft_ax.clear()
        self.fft_ax.bar(freqs[:len(freqs)//2], np.abs(fft_data)[:len(fft_data)//2], width=0.5)
        self.fft_ax.set_title("FFT Analysis")
        self.fft_ax.set_xlabel("Frequency (Hz)")
        self.fft_ax.set_ylabel("Amplitude")
        self.fft_canvas.draw()

        # Update status
        status = "Normal" if random.random() > 0.2 else "Abnormal"
        self.status_label.config(text=f"Status: {status}", 
                                 foreground="green" if status == "Normal" else "red")

        # Schedule next update
        self.master.after(1000, self.update)

root = tk.Tk()
dashboard = VibrationDashboard(root)
root.mainloop()