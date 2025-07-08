# noise2signal Full Function GUI

A standalone desktop application built with Tkinter for denoising and frequency-compressing audio files using spectral processing techniques.

## Features

- **Load and visualize**: Display original waveform and spectrogram of any WAV file.
- **Denoise**: Interactive control over multiple parameters for spectral ridge detection and masking.
- **Frequency Compression**: Lower the perceived frequency of the denoised audio by an arbitrary factor.
- **Playback**: Play compressed audio directly from the GUI.
- **Configurable**: Enable or disable each denoising parameter via checkboxes.
- **Visual comparison**: Six-panel canvas showing original, denoised, and compressed waveforms and spectrograms.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/noise2signal.git
   cd noise2signal
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install numpy scipy librosa soundfile matplotlib
   ```

> **Note**: `tkinter` is included in most Python distributions. If you encounter issues, install your OS package (e.g., `sudo apt-get install python3-tk`).

## Usage

Run the GUI script:

```bash
python noise2signal_gui.py
```

1. **Select Audio File**: Click to browse and choose a WAV file.
2. **Load**: Load the selected file and display its original waveform and spectrogram.
3. **Denise Parameters**: Adjust parameters in the left panel; use checkboxes to enable or disable each.
4. **Convert**: Perform denoising; results appear in the next row of plots.
5. **Compression Factor**: Enter an integer factor (default `10`) to lower the frequency by that multiple.
6. **Compression**: Apply frequency compression; results appear in the bottom row of plots.
7. **Play Audio**: Play the compressed audio (`mouse_perceptually_compressed.wav`) using the system's default player.

## Denoise Parameters

| Parameter                 | Default | Description                               |
| ------------------------- | ------- | ----------------------------------------- |
| `alpha`                   | 0.5     | Bandwidth scaling for continuous mask     |
| `keep_ratio`              | 0.8     | Threshold ratio for ridge bandwidth       |
| `num_peaks`               | 4       | Number of peaks for peak mask             |
| `peak_width_hz`           | 5       | Width (Hz) for each peak in peak mask     |
| `soft_alpha`              | 0.001   | Bandwidth softening factor                |
| `power_threshold_db`      | 6       | dB threshold above baseline for activity  |
| `min_segment_length`      | 15      | Minimum length of active segment (frames) |
| `drop_db_threshold`       | 10      | dB drop to mark unreliable ridge          |
| `freq_jump_threshold`     | 2000    | Max allowed ridge frequency jump (Hz)     |
| `min_bandwidth`           | 500.0   | Minimum allowed bandwidth (Hz)            |
| `max_bandwidth`           | 10000.0 | Maximum allowed bandwidth (Hz)            |
| `bandwidth_smooth_window` | 7       | Smoothing window size for bandwidth       |
| `mask_contribution`       | 0.7     | Weight of continuous mask                 |
| `mask_peak_contribution`  | 0.3     | Weight of peak mask                       |
| `mask_smoothing`          | True    | Enable smoothing of the combined mask     |
| `mask_smooth_window`      | 5       | Smoothing window size for mask            |

## Output

- **Compressed audio**: `mouse_perceptually_compressed.wav` saved in the working directory after compression.

## License

This project is released under the MIT License. See [LICENSE](LICENSE) for details.
