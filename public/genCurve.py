import matplotlib.pyplot as plt
from astropy.io import fits
import os
import numpy as np

def count(folder_path):
    """Count the number of files in the specified folder."""
    items = os.listdir(folder_path)
    files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
    return len(files)

def moving_average(data, window_size):
    """Calculate the moving average of the given data."""
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def plot_light_curve(folder_path, output_history, output_mov_avg, window_size=500):
    """Load light curve FITS file, plot original and moving average, and save images."""
    i = count(folder_path)

    # Load the light curve FITS file
    with fits.open(os.path.join(folder_path, f'data{i-1}.lc')) as hdul:
        data = hdul[1].data  # Light curve data is usually in the second extension
        time = data['TIME']
        rate = data['RATE']

    # Plot the original light curve
    plt.figure(figsize=(10, 6))
    plt.plot(time, rate, label='Original Rate', color='blue', alpha=0.6)
    plt.xlabel('Time (s)')
    plt.ylabel('Rate (counts/s)')
    plt.title('XSM Light Curve')
    plt.savefig(os.path.join(output_history, f'img{i-1}.png'))
    plt.close()  # Close the plot to free memory

    # Compute and plot the moving average
    rate_smooth = moving_average(rate, window_size)
    time_smooth = time[window_size - 1:]  # Adjust time array to fit the shorter smoothed data

    plt.figure(figsize=(10, 6))
    plt.plot(time_smooth, rate_smooth, label=f'Moving Average (window={window_size})', color='red', linewidth=1)
    plt.xlabel('Time (s)')
    plt.ylabel('Rate (counts/s)')
    plt.title('XSM Light Curve with Moving Average')
    plt.legend()
    plt.savefig(os.path.join(output_mov_avg, f'img{i-1}.png'))
    plt.close()  # Close the plot to free memory

# Define paths
folder_path = './uploads/'
output_history = './public/history/'
output_mov_avg = './public/movAvg/'

# Ensure output directories exist
os.makedirs(output_history, exist_ok=True)
os.makedirs(output_mov_avg, exist_ok=True)

# Call the function to plot light curves
plot_light_curve(folder_path, output_history, output_mov_avg)
