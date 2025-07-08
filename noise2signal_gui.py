import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import librosa
from scipy.signal import stft
import matplotlib as mpl
import soundfile as sf
import os
import subprocess
import platform

class Untitled4FullGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("noise2signal full function GUI")
        self.geometry("1300x800")
        self.audio_path = None
        # Only keep audio analysis parameters
        self.factor = tk.IntVar(value=10)
        # denoise parameter
        self.alpha = tk.DoubleVar(value=0.5)
        self.keep_ratio = tk.DoubleVar(value=0.8)
        self.num_peaks = tk.IntVar(value=4)
        self.peak_width_hz = tk.DoubleVar(value=5)
        self.soft_alpha = tk.DoubleVar(value=0.001)
        self.power_threshold_db = tk.DoubleVar(value=6)
        self.min_segment_length = tk.IntVar(value=15)
        self.drop_db_threshold = tk.DoubleVar(value=10)
        self.freq_jump_threshold = tk.DoubleVar(value=2000)
        self.min_bandwidth = tk.DoubleVar(value=500.0)
        self.max_bandwidth = tk.DoubleVar(value=10000.0)
        self.bandwidth_smooth_window = tk.IntVar(value=7)
        self.mask_contribution = tk.DoubleVar(value=0.7)
        self.mask_peak_contribution = tk.DoubleVar(value=0.3)
        self.mask_smoothing = tk.BooleanVar(value=True)
        self.mask_smooth_window = tk.IntVar(value=5)
        
        # Add enable/disable checkboxes for each parameter (except mask_smoothing and factor)
        self.alpha_enabled = tk.BooleanVar(value=True)
        self.keep_ratio_enabled = tk.BooleanVar(value=True)
        self.num_peaks_enabled = tk.BooleanVar(value=True)
        self.peak_width_hz_enabled = tk.BooleanVar(value=True)
        self.soft_alpha_enabled = tk.BooleanVar(value=True)
        self.power_threshold_db_enabled = tk.BooleanVar(value=True)
        self.min_segment_length_enabled = tk.BooleanVar(value=True)
        self.drop_db_threshold_enabled = tk.BooleanVar(value=True)
        self.freq_jump_threshold_enabled = tk.BooleanVar(value=True)
        self.min_bandwidth_enabled = tk.BooleanVar(value=True)
        self.max_bandwidth_enabled = tk.BooleanVar(value=True)
        self.bandwidth_smooth_window_enabled = tk.BooleanVar(value=True)
        self.mask_contribution_enabled = tk.BooleanVar(value=True)
        self.mask_peak_contribution_enabled = tk.BooleanVar(value=True)
        self.mask_smooth_window_enabled = tk.BooleanVar(value=True)
        # Place the select audio file button and file label at the top
        tk.Button(self, text="Select Audio File", command=self.select_audio).place(x=20, y=20, width=120, height=30)
        self.file_path_var = tk.StringVar(value="No file selected")
        self.file_entry = tk.Entry(self, textvariable=self.file_path_var)
        self.file_entry.place(x=150, y=20, width=400, height=30)
        # Move Load button to the right of file_entry
        tk.Button(self, text="Load", command=self.load_audio).place(x=560, y=20, width=80, height=30)
        # All denoise parameters in a single column, entry below label
        small_font = ("Arial", 10)
        denoise_param_vars = [
            ("alpha", self.alpha, "Bandwidth scaling for continuous mask", self.alpha_enabled),
            ("keep_ratio", self.keep_ratio, "Threshold ratio for ridge bandwidth", self.keep_ratio_enabled),
            ("num_peaks", self.num_peaks, "Number of peaks for peak mask", self.num_peaks_enabled),
            ("peak_width_hz", self.peak_width_hz, "Width (Hz) for each peak in peak mask", self.peak_width_hz_enabled),
            ("soft_alpha", self.soft_alpha, "Bandwidth softening factor", self.soft_alpha_enabled),
            ("power_threshold_db", self.power_threshold_db, "dB threshold above baseline for activity", self.power_threshold_db_enabled),
            ("min_segment_length", self.min_segment_length, "Minimum length of active segment", self.min_segment_length_enabled),
            ("drop_db_threshold", self.drop_db_threshold, "dB drop to mark unreliable ridge", self.drop_db_threshold_enabled),
            ("freq_jump_threshold", self.freq_jump_threshold, "Max allowed ridge frequency jump (Hz)", self.freq_jump_threshold_enabled),
            ("min_bandwidth", self.min_bandwidth, "Minimum allowed bandwidth (Hz)", self.min_bandwidth_enabled),
            ("max_bandwidth", self.max_bandwidth, "Maximum allowed bandwidth (Hz)", self.max_bandwidth_enabled),
            ("bandwidth_smooth_window", self.bandwidth_smooth_window, "Smoothing window for bandwidth", self.bandwidth_smooth_window_enabled),
            ("mask_contribution", self.mask_contribution, "Weight of continuous mask", self.mask_contribution_enabled),
            ("mask_peak_contribution", self.mask_peak_contribution, "Weight of peak mask", self.mask_peak_contribution_enabled),
            ("mask_smoothing", self.mask_smoothing, "Enable mask smoothing", None),  # No enable checkbox for this one
            ("mask_smooth_window", self.mask_smooth_window, "Smoothing window for mask", self.mask_smooth_window_enabled)
        ]
        y_base = 70
        y_step = 35  # Slightly reduced step to fit more parameters
        for i, param_info in enumerate(denoise_param_vars):
            if len(param_info) == 4:
                name, var, expl, enable_var = param_info
            else:
                name, var, expl = param_info
                enable_var = None
                
            y_label = y_base + i * y_step
            y_entry = y_label + 16
            label_text = name+":"
            if expl:
                label_text += f"  ({expl})"
            tk.Label(self, text=label_text, font=small_font, anchor='w', justify='left').place(x=20, y=y_label)
            
            if isinstance(var, tk.BooleanVar):
                tk.Checkbutton(self, variable=var).place(x=20, y=y_entry)
            else:
                tk.Entry(self, textvariable=var, width=6, font=small_font).place(x=20, y=y_entry)
                # Add enable/disable checkbox next to the entry (except for mask_smoothing)
                if enable_var is not None:
                    tk.Checkbutton(self, variable=enable_var, width=6, font=small_font).place(x=100, y=y_entry)
        
        # Calculate button positions
        buttons_y_start = y_base + len(denoise_param_vars) * y_step + 20
        
        # Add Convert button (top)
        tk.Button(self, text="Convert", command=self.convert_denoise_audio).place(x=20, y=buttons_y_start, width=120, height=36)
        
        # Add Compression factor between the two buttons
        factor_y = buttons_y_start + 50
        tk.Label(self, text="Compression factor:", font=small_font).place(x=20, y=factor_y)
        tk.Entry(self, textvariable=self.factor, width=6, font=small_font).place(x=20, y=factor_y+16)
        
        # Add Compression button (bottom)
        tk.Button(self, text="Compression", command=self.compress_audio).place(x=20, y=factor_y+50, width=120, height=36)
        
        # Add Play Audio button below compression button
        tk.Button(self, text="Play Audio", command=self.play_compressed_audio).place(x=20, y=factor_y+95, width=120, height=30)
        # Canvas with 6 subplots (3 rows, 2 columns)
        self.fig = plt.Figure(figsize=(12,9))
        self.axarr = [self.fig.add_subplot(3,2,i+1) for i in range(6)]
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().place(x=350, y=60, width=900, height=700)

    def select_audio(self):
        path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if path:
            self.audio_path = path
            self.file_path_var.set(path)

    def load_audio(self):
        file_path = self.file_path_var.get().strip()
        if not file_path or file_path == "No file selected":
            messagebox.showwarning("No file selected", "Please select an audio file first!")
            return
        try:
            # Load audio and show original waveform and spectrogram
            y, sr = librosa.load(file_path, sr=None)
            self.y = y
            self.sr = sr
            self.audio_path = file_path  # Update for compatibility
            # Clear all subplots and show only original waveform and spectrogram
            for ax in self.axarr:
                ax.clear()
            self.axarr[0].plot(np.arange(len(y)) / sr, y)
            self.axarr[0].set_title("Original Waveform")
            self.axarr[1].specgram(y, NFFT=1024, Fs=sr, noverlap=512, cmap='magma')
            self.axarr[1].set_title("Original Spectrogram")
            self.fig.tight_layout()
            self.canvas.draw()
        except Exception as e:
            messagebox.showerror("Error loading file", f"Failed to load audio file:\n{str(e)}")

    def denoise_audio(self, y, sr):
        # Read parameters and their enable status
        alpha = self.alpha.get() if self.alpha_enabled.get() else 0.5
        keep_ratio = self.keep_ratio.get() if self.keep_ratio_enabled.get() else 0.8
        num_peaks = self.num_peaks.get() if self.num_peaks_enabled.get() else 4
        peak_width_hz = self.peak_width_hz.get() if self.peak_width_hz_enabled.get() else 5
        soft_alpha = self.soft_alpha.get() if self.soft_alpha_enabled.get() else 0.001
        power_threshold_db = self.power_threshold_db.get() if self.power_threshold_db_enabled.get() else 6
        min_segment_length = self.min_segment_length.get() if self.min_segment_length_enabled.get() else 15
        drop_db_threshold = self.drop_db_threshold.get() if self.drop_db_threshold_enabled.get() else 10
        freq_jump_threshold = self.freq_jump_threshold.get() if self.freq_jump_threshold_enabled.get() else 2000
        min_bandwidth = self.min_bandwidth.get() if self.min_bandwidth_enabled.get() else 500.0
        max_bandwidth = self.max_bandwidth.get() if self.max_bandwidth_enabled.get() else 10000.0
        bandwidth_smooth_window = self.bandwidth_smooth_window.get() if self.bandwidth_smooth_window_enabled.get() else 7
        mask_contribution = self.mask_contribution.get() if self.mask_contribution_enabled.get() else 0.7
        mask_peak_contribution = self.mask_peak_contribution.get() if self.mask_peak_contribution_enabled.get() else 0.3
        mask_smoothing = self.mask_smoothing.get()  # This one doesn't have an enable checkbox
        mask_smooth_window = self.mask_smooth_window.get() if self.mask_smooth_window_enabled.get() else 5
        nfft = 2048
        win_length = 256
        hop_length = 64
        overlap = win_length - hop_length
        window = np.hanning(win_length)
        f_spec, t_spec, S = stft(y, fs=sr, window=window,
                                 nperseg=win_length, noverlap=overlap,
                                 nfft=nfft, boundary=None)
        mag = np.abs(S)
        ridge_bins = np.argmax(mag, axis=0)
        ridge_freq = f_spec[ridge_bins]
        bandwidth = np.zeros_like(ridge_freq)
        for t in range(len(t_spec)):
            spec_frame = mag[:, t]
            rb = ridge_bins[t]
            thr = keep_ratio * spec_frame[rb]
            bins = [rb]
            k = 1
            while rb + k < mag.shape[0] and spec_frame[rb + k] > thr:
                bins.append(rb + k); k += 1
            k = 1
            while rb - k >= 0 and spec_frame[rb - k] > thr:
                bins.append(rb - k); k += 1
            sel = np.array(bins, dtype=int)
            w_spec = spec_frame[sel]
            w_freqs = f_spec[sel]
            if w_spec.sum() > 0:
                m_f = np.sum(w_freqs * w_spec) / w_spec.sum()
                var_f = np.sum(w_spec * (w_freqs - m_f)**2) / w_spec.sum()
                bandwidth[t] = np.sqrt(max(var_f, 0))
            else:
                bandwidth[t] = min_bandwidth
        if bandwidth_smooth_window > 1:
            from scipy.ndimage import uniform_filter1d
            bandwidth = np.convolve(bandwidth, np.ones(bandwidth_smooth_window)/bandwidth_smooth_window, mode='same')
        bandwidth = np.clip(bandwidth, min_bandwidth, max_bandwidth)
        ridge_pow = mag[ridge_bins, np.arange(len(t_spec))]
        baseline = np.mean(ridge_pow[t_spec <= 0.1]) if np.any(t_spec <= 0.1) else np.mean(ridge_pow)
        power_thr = baseline * 10**(power_threshold_db/10)
        active = ridge_pow > power_thr
        active_idx = np.where(active)[0]
        if active_idx.size > 0:
            breaks = np.where(np.diff(active_idx) > 1)[0] + 1
            segs = np.split(active_idx, breaks)
            call_frames = np.concatenate([seg for seg in segs if len(seg) > min_segment_length])
        else:
            call_frames = np.array([], dtype=int)
        ridge_db = 10 * np.log10(ridge_pow + np.finfo(float).eps)
        if active_idx.size > 0:
            med_db = np.median(ridge_db[active_idx])
            drop_db = med_db - drop_db_threshold
            bad = np.zeros_like(ridge_freq, bool)
            for t in range(1, len(ridge_freq)-1):
                if ridge_db[t] < drop_db:
                    pf, nf, cf = ridge_freq[t-1], ridge_freq[t+1], ridge_freq[t]
                    if (np.isnan(pf) or np.isnan(nf) or abs(cf-pf) > freq_jump_threshold or abs(cf-nf) > freq_jump_threshold):
                        bad[t] = True
            ridge_freq[bad] = np.nan
            for t in range(1, len(bandwidth)-1):
                if ridge_db[t] < drop_db and not np.isnan(ridge_freq[t]):
                    lo, hi = max(0, t-2), min(len(bandwidth), t+3)
                    bandwidth[t] = np.nanmedian(bandwidth[lo:hi])
        alpha_dyn = alpha + soft_alpha * bandwidth
        mask_cont = np.zeros_like(mag, bool)
        mask_peak = np.zeros_like(mag, bool)
        bin_hz = sr / nfft
        w5 = int(round(peak_width_hz / bin_hz))
        for t in range(len(t_spec)):
            if not np.isnan(ridge_freq[t]):
                low = ridge_freq[t] - alpha_dyn[t]*bandwidth[t]
                high = ridge_freq[t] + alpha_dyn[t]*bandwidth[t]
                mask_cont[:,t] = (f_spec >= low) & (f_spec <= high)
            if t in call_frames:
                idxs = np.argpartition(mag[:,t], -num_peaks)[-num_peaks:]
                for b in idxs:
                    lo, hi = max(0, b-w5), min(mag.shape[0], b+w5+1)
                    mask_peak[lo:hi,t] = True
        mask_cont_weighted = mask_contribution * mask_cont.astype(float)
        mask_peak_weighted = mask_peak_contribution * mask_peak.astype(float)
        mask_bin = (mask_cont_weighted + mask_peak_weighted) > 0.5
        if mask_smoothing and mask_smooth_window > 1:
            from scipy.ndimage import uniform_filter1d
            mask_bin = uniform_filter1d(mask_bin.astype(float), size=mask_smooth_window, axis=1) > 0.5
        return S, mask_bin, f_spec, t_spec, nfft, win_length, hop_length

    def convert_denoise_audio(self):
        if not hasattr(self, 'y') or not hasattr(self, 'sr'):
            messagebox.showwarning("No audio selected", "Please select an audio file first!")
            return
        
        y = self.y
        sr = self.sr
        S, mask_bin, f_spec, t_spec, nfft, win_length, hop_length = self.denoise_audio(y, sr)
        
        # Store denoised data for compression
        self.S_denoised = S * mask_bin
        self.mask_bin = mask_bin
        self.nfft = nfft
        self.win_length = win_length
        self.hop_length = hop_length
        
        # Reconstruct denoised audio
        y_denoised = librosa.istft(S * mask_bin, hop_length=hop_length, win_length=win_length, window='hann', length=len(y))
        self.y_denoised = y_denoised
        
        # Display denoised waveform and spectrogram in subplots 2,3 (index 2,3)
        self.axarr[2].clear()
        self.axarr[3].clear()
        self.axarr[2].plot(np.arange(len(y_denoised)) / sr, y_denoised)
        self.axarr[2].set_title("Denoised Waveform")
        
        # Apply the same visual enhancement to denoised spectrogram
        Pxx_denoised, freqs_denoised, bins_denoised, _ = plt.specgram(
            y_denoised,
            NFFT=1024,
            Fs=sr,
            noverlap=512,
            cmap='magma'
        )
        Pxx_denoised_dB = 10 * np.log10(Pxx_denoised + 1e-12)
        vmin_denoised = np.percentile(Pxx_denoised_dB, 95)
        cmap_denoised = plt.get_cmap('magma').copy()
        cmap_denoised.set_bad('black')
        masked_Pxx_denoised_dB = np.ma.masked_where(Pxx_denoised_dB < vmin_denoised, Pxx_denoised_dB)
        
        self.axarr[3].pcolormesh(bins_denoised, freqs_denoised, masked_Pxx_denoised_dB, cmap=cmap_denoised)
        self.axarr[3].set_title("Denoised Spectrogram")
        self.fig.tight_layout()
        self.canvas.draw()

    def compress_audio(self):
        if not hasattr(self, 'S_denoised') or not hasattr(self, 'sr'):
            messagebox.showwarning("No denoised audio", "Please run Convert first to denoise the audio!")
            return
        
        factor = self.factor.get()
        sr = self.sr
        
        # Use the stored denoised STFT data
        S_masked = self.S_denoised
        hop_length = self.hop_length
        win_length = self.win_length
        
        # Apply frequency compression
        hop_length_new = max(1, int(hop_length / factor))
        sr_new = max(1, int(sr / factor))
        
        y_compressed = librosa.istft(S_masked,
                                     hop_length=hop_length_new,
                                     win_length=win_length,
                                     window='hann')
        y_compressed = y_compressed / np.max(np.abs(y_compressed)) * 0.99
        self.y_compressed = y_compressed
        self.sr_compressed = sr_new
        
        # Calculate spectrogram parameters for compressed signal
        nfft_comp = int(round(self.nfft / factor))
        hop_comp = int(round(hop_length * 8 / factor))
        noverlap_comp = nfft_comp - hop_comp
        
        Pxx, freqs, bins, _ = plt.specgram(
            y_compressed,
            NFFT=nfft_comp,
            Fs=sr_new,
            noverlap=noverlap_comp,
            cmap='magma'
        )
        Pxx_dB = 10 * np.log10(Pxx + 1e-12)
        vmin = np.percentile(Pxx_dB, 95)
        cmap = plt.get_cmap('magma').copy()
        cmap.set_bad('black')
        masked_Pxx_dB = np.ma.masked_where(Pxx_dB < vmin, Pxx_dB)
        
        # Display compressed waveform and spectrogram in subplots 4,5 (index 4,5)
        self.axarr[4].clear()
        self.axarr[5].clear()
        self.axarr[4].plot(np.arange(len(y_compressed)) / sr_new, y_compressed)
        self.axarr[4].set_title("Compressed Waveform")
        self.axarr[5].pcolormesh(bins, freqs, masked_Pxx_dB, cmap=cmap)
        self.axarr[5].set_title("Compressed Spectrogram")
        self.fig.tight_layout()
        self.canvas.draw()
        
        # Save compressed audio
        sf.write("mouse_perceptually_compressed.wav", y_compressed, sr_new)



    def play_compressed_audio(self):
        audio_file = "mouse_perceptually_compressed.wav"
        if not os.path.exists(audio_file):
            messagebox.showwarning("File not found", "Please generate analysis plots first!")
            return
        
        try:
            if platform.system() == "Darwin":  # macOS
                subprocess.run(["open", audio_file])
            elif platform.system() == "Windows":
                subprocess.run(["start", audio_file], shell=True)
            else:  # Linux
                subprocess.run(["xdg-open", audio_file])
            messagebox.showinfo("Playing Audio", f"Opening {audio_file} with default player...")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to play audio: {str(e)}")

if __name__ == "__main__":
    app = Untitled4FullGUI()
    app.mainloop() 