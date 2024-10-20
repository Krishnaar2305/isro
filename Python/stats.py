import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import find_peaks, peak_prominences
import pandas as pd
import os
import json
from datetime import datetime

MIN_MA_WINDOW_SZ = 10  # Moving average window size
MIN_MULTIPLIER = 4  # minimum multiplication factor used in filter 4
IF_N_ESTIMATORS = 100  # used in Isolation classifier
IF_CONTAMINATION = 0.01  # used in Isolation classifier
IF_MAX_FEATURES = 5  # used in Isolation classifier
THRESHOLD_Y_NOISE_LVL5 =  1000 # threshold for filtering out too near-in-y flares
THRESHOLD_X_NOISE_LVL5 = 1000  # threshold for filtering out too near-in-x flares
MAX_WINDOW_SIZE = 120  # max window size used in moving average
MIN_WINDOW_SIZE = 100  # min  window size used in moving average
MINIMUM_DATAPOINTS_IN_GTI = 120  # minimum data points needed in discontinuous intervals
SIGMOID_SHIFT_WINDOW_SIZE = 240  # window size origin shift for sigmoid

K = 0.5

def del_files(folder_path):
    # Loop through all files in the specified folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        # Check if it's a file
        if os.path.isfile(file_path):
            os.remove(file_path)

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

def smoothen_fft_(lc, thresh=100):
    # a low pass filter
    lc_fft = np.fft.fft(lc)
    lc_fft[thresh : len(lc) - thresh] = 0 
    lc_smooth = np.abs(np.fft.ifft(lc_fft))
    return lc_smooth

def smoothen_moving_mean(lc, window_sz=100, shift=20, should_plot=False, s=0.3, interp_method='linear'):
    new_norm = np.ones(len(lc))
    num_frames = 0
    # first frame
    num_frames += 1
    tmp = np.mean(lc[0:window_sz])
    new_norm[0:window_sz] *= tmp
    # rest frames
    for i in range(window_sz, len(lc), shift):
        num_frames += 1
        tmp = np.mean(lc[i:i+window_sz])
        new_norm[i:i+window_sz] = 1
        new_norm[i:i+window_sz] *= tmp

    # Handling gaps or missing data using linear interpolation
    x_valid = np.arange(len(new_norm))  # Create an array of valid indices
    y_valid = new_norm                  # The smoothed data

    # Define the interpolator (linear by default, can be modified to other methods)
    interpolator = interp1d(x_valid, y_valid, kind=interp_method, fill_value="extrapolate")

    # Interpolate over the full range
    new_norm_interp = interpolator(np.arange(len(lc)))

    if should_plot:
        plt.figure(figsize=(25, 7))
        plt.grid()
        plt.scatter(range(len(new_norm_interp)), new_norm_interp, s=s)
    
    return new_norm_interp

def get_slope(x1, x2, y1, y2):
    return (y1 - y2) / (x1 - x2)

def euclidean(x1, x2, y1, y2):
    _y = (y1 - y2) * (y1 - y2)
    _x = (x1 - x2) * (x1 - x2)
    return np.sqrt(_x + _y)

def exp_fit_func(x, ln_a, b):
    t = x**K
    return ln_a - b * t

def exp_func(x, a, b):
    t = -1 * b * (x**K)
    return a * np.exp(t)

def inverse_exp_func(y, a, b):
    t1 = np.log(y) - np.log(a)
    t2 = -1 * t1 / b
    return int(t2 ** (1.0 / K))


def get_lvl_0_sp_(xnew, ynew, should_plot=False):
    """Detection of all Minima and Maxima"""
    _p0, _ = find_peaks(ynew)
    _s0, _ = find_peaks(-ynew)
    
    if should_plot:
        plt.figure(figsize=(30, 10))
        plt.title("Level 0 Maxima and Minima")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p0], ynew[_p0], "ro", label="Maxima")
        plt.plot(xnew[_s0], ynew[_s0], "bx", label="Minima")
        plt.legend()
        plt.show()
    
    return _s0, _p0

def get_lvl_1_sp_(xnew, ynew, _s0, _p0, should_plot=False):
    """Pairing of minima and maxima as starts and peaks"""
    _s1, _p1 = [], []
    for peak in _p0:
        start = _s0[_s0 < peak][-1] if any(_s0 < peak) else _s0[0]
        _s1.append(start)
        _p1.append(peak)
    
    if should_plot:
        plt.figure(figsize=(30, 10))
        plt.title("Level 1 Maxima and Minima")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p1], ynew[_p1], "ro", label="Maxima")
        plt.plot(xnew[_s1], ynew[_s1], "bx", label="Minima")
        plt.legend()
        plt.show()
    
    return _s1, _p1

def get_slope(x1, x2, y1, y2):
    return (y2 - y1) / (x2 - x1) if x2 != x1 else 0

def get_lvl_2_sp_(xnew, ynew, _s1, _p1, should_plot=False):
    """Slope and prominence thresholding"""
    _slopes = np.array([get_slope(xnew[s], xnew[p], ynew[s], ynew[p]) for s, p in zip(_s1, _p1)])
    prominences = peak_prominences(ynew, _p1)[0]
    
    mean_sl = np.mean(_slopes)
    mean_prom = np.mean(prominences)
    
    _s2 = [s for s, slope, prom in zip(_s1, _slopes, prominences) if slope > mean_sl * 0.5 and prom > mean_prom * 0.5]
    _p2 = [p for p, slope, prom in zip(_p1, _slopes, prominences) if slope > mean_sl * 0.5 and prom > mean_prom * 0.5]
    
    if should_plot:
        plt.figure(figsize=(30, 10))
        plt.title("Level 2 Maxima and Minima")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p2], ynew[_p2], "ro", label="Maxima")
        plt.plot(xnew[_s2], ynew[_s2], "bx", label="Minima")
        plt.legend()
        plt.show()
    
    return _s2, _p2

def get_lvl_3_sp_(xnew, ynew, _s2, _p2, f, should_plot=False):
    """Height and width thresholding"""
    heights = [ynew[p] - ynew[s] for s, p in zip(_s2, _p2)]
    widths = [xnew[p] - xnew[s] for s, p in zip(_s2, _p2)]
    
    mean_height = np.mean(heights)
    mean_width = np.mean(widths)
    
    _s3 = [s for s, p, h, w in zip(_s2, _p2, heights, widths) if h > mean_height * f * 0.5 and w > mean_width * 0.5]
    _p3 = [p for s, p, h, w in zip(_s2, _p2, heights, widths) if h > mean_height * f * 0.5 and w > mean_width * 0.5]
    
    if should_plot:
        plt.figure(figsize=(30, 10))
        plt.title("Level 3 Maxima and Minima")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p3], ynew[_p3], "ro", label="Maxima")
        plt.plot(xnew[_s3], ynew[_s3], "bx", label="Minima")
        plt.legend()
        plt.show()
    
    return _s3, _p3

def get_lvl_4_sp_(xnew, ynew, _s3, _p3, should_plot=False):
    """Unique starts and peaks"""
    s = set()
    _s4, _p4 = [], []
    for start, peak in zip(_s3, _p3):
        if start not in s:
            s.add(start)
            _s4.append(start)
            _p4.append(peak)
    
    if should_plot:
        plt.figure(figsize=(30, 10))
        plt.title("Level 4 Maxima and Minima")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p4], ynew[_p4], "ro", label="Maxima")
        plt.plot(xnew[_s4], ynew[_s4], "bx", label="Minima")
        plt.legend()
        plt.show()
    
    return _s4, _p4

def get_lvl_5_sp_(xnew, ynew, _s4, _p4, should_plot=False):
    """Filter for too close peaks while preserving significant ones"""
    THRESHOLD_X_NOISE_LVL5 = np.mean(np.diff(xnew)) * 2  # Adjust this value as needed
    THRESHOLD_Y_NOISE_LVL5 = np.std(ynew) * 0.5  # Adjust this value as needed
    
    to_remove = []
    for i in range(len(_p4) - 1):
        if (xnew[_p4[i+1]] - xnew[_p4[i]] < THRESHOLD_X_NOISE_LVL5):
            if np.abs(ynew[_p4[i+1]] - ynew[_p4[i]]) < THRESHOLD_Y_NOISE_LVL5:
                to_remove.append(i if ynew[_p4[i+1]] > ynew[_p4[i]] else i+1)
            else:
                # Keep both peaks if they're significantly different in height
                continue
    
    _s5 = [s for i, s in enumerate(_s4) if i not in to_remove]
    _p5 = [p for i, p in enumerate(_p4) if i not in to_remove]
    
    if should_plot:
        plt.figure(figsize=(30, 10))
        plt.title("Level 5 Maxima and Minima")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p5], ynew[_p5], "ro", label="Maxima")
        plt.plot(xnew[_s5], ynew[_s5], "bx", label="Minima")
        plt.legend()
        plt.show()
    
    return _s5, _p5

def get_lvl_0_e_(xnew, ynew, _s5, _p5, _s0, should_plot=False):
    """Find end points"""
    _e0 = []
    for i, peak in enumerate(_p5):
        end_candidates = []
        for j in range(peak, len(xnew)):
            if ynew[j] < (ynew[peak] + ynew[_s5[i]]) / 2:
                end_candidates.append(j)
            if i + 1 < len(_s5) and xnew[j] > xnew[_s5[i + 1]]:
                break
            if j == len(xnew) - 1:
                end_candidates.append(j)
        
        if end_candidates:
            _e0.append(max(end_candidates, key=lambda x: ynew[x]))
        else:
            _e0.append(len(xnew) - 1)
    
    if should_plot:
        plt.figure(figsize=(30, 10))
        plt.title("Level 0 Ends")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p5], ynew[_p5], "ro", label="Peaks")
        plt.plot(xnew[_e0], ynew[_e0], "gx", label="Ends")
        plt.legend()
        plt.show()
    
    return _e0

def get_lvl_1_e_(xnew, ynew, _s0, _p5, _e0, output_dir, should_plot=False):
    """Refine end points"""
    _e1 = []
    for i, (peak, end) in enumerate(zip(_p5, _e0)):
        if ynew[end] < ynew[peak]:
            _e1.append(end)
        else:
            # Find the first minimum after the peak
            for j in range(peak, len(xnew)):
                if j in _s0:
                    _e1.append(j)
                    break
            else:
                _e1.append(end)  # If no minimum is found, keep the original end
    
    if should_plot:
        plt.figure(figsize=(10, 4))
        plt.title("Level 1 Ends")
        plt.plot(xnew, ynew, label="Light Curve")
        plt.plot(xnew[_p5], ynew[_p5], "ro", label="Peaks")
        plt.plot(xnew[_e1], ynew[_e1], "gx", label="Refined Ends")
        plt.legend()
        plt.savefig(os.path.join(output_dir, f'peaksCurve{now}.png'))
        plt.close()
        # plt.show()
    
    return np.array(_e1)

# def count(folder_path):
#     """Count the number of files in the specified folder."""
#     items = os.listdir(folder_path)
#     files = [item for item in items if os.path.isfile(os.path.join(folder_path, item))]
#     return len(files)

folder_path = './uploads/'
output_dir = "./public/curves/"

del_files(output_dir)
now = int(datetime.now().timestamp())


# output_history = './public/history/'
# output_smoothened = './public/smoothened/'
# output_peaks = './public/peaks/'

# fileCount = count(folder_path)

with fits.open(f'uploads/data.lc') as hdul:
    data = hdul[1].data  
    time = data['TIME']
    rate = data['RATE']
window_size = 100  

plt.figure(figsize=(10, 4))
plt.xlabel('Time (s)')
plt.ylabel('Rate (counts/s)')
plt.title('XSM Light Curve')
plt.plot(time, rate)
plt.savefig(os.path.join(output_dir, f'originalCurve{now}.png'))
plt.close()

rate_smooth = smoothen_moving_mean(rate, window_sz=window_size, should_plot=False)
rate_smooth=smoothen_fft_(rate_smooth)
time_smooth = np.arange(0, len(rate_smooth))

plt.figure(figsize=(10, 4))
plt.xlabel('Time (s)')
plt.ylabel('Rate (counts/s)')
plt.title('XSM Light Curve after Smoothening')
plt.plot(time_smooth, rate_smooth)
plt.savefig(os.path.join(output_dir, f'smoothenedCurve{now}.png'))
plt.close()

should_plot = False
xnew=time_smooth
ynew=rate_smooth
f=0.3
s0, p0 = get_lvl_0_sp_(xnew, ynew, should_plot)
s1, p1 = get_lvl_1_sp_(xnew, ynew, s0, p0, should_plot)
s2, p2 = get_lvl_2_sp_(xnew, ynew, s1, p1, should_plot)
s3, p3 = get_lvl_3_sp_(xnew, ynew, s2, p2, f, should_plot)
s4, p4 = get_lvl_4_sp_(xnew, ynew, s3, p3, should_plot)
s5, p5 = get_lvl_5_sp_(xnew, ynew, s4, p4, should_plot)
e0 = get_lvl_0_e_(xnew, ynew, s5, p5, s0, should_plot)
e1 = get_lvl_1_e_(xnew, ynew, s0, p5, e0, output_dir, should_plot)

plt.figure(figsize=(10, 4))
plt.xlabel('Time (s)')
plt.ylabel('Rate (counts/s)')
plt.title("Final Detection Results")
plt.plot(xnew, ynew, label="Light Curve")
plt.plot(xnew[p5], ynew[p5], "ro", label="Peaks")
plt.plot(xnew[s5], ynew[s5], "bx", label="Starts")
plt.plot(xnew[e1], ynew[e1], "gx", label="Ends")
plt.legend()
plt.savefig(os.path.join(output_dir, f'peaksCurve{now}.png'))
plt.close()

df1 = pd.DataFrame(columns=['start_time', 'end_time', 'peak_time', 'start_value','end_value','peak_value','burst_duration','burst_amplitude'])
df1['start_time'] = s5
df1['end_time'] = e1
df1['peak_time'] = p5
df1['peak_value'] = rate_smooth[p5]
df1['start_value'] = rate_smooth[s5]
df1['end_value'] = rate_smooth[e1]
df1['burst_duration'] = time_smooth[e1] - time_smooth[s5]
df1['burst_amplitude'] = rate_smooth[p5] - rate_smooth[s5]
# df=pd.concat([df,df1])
# print(df.describe(include='all'))
result = {
    "now" : now,
    "start_time": df1["start_time"].tolist(),
    "end_time": df1["end_time"].tolist(),
    "peak_time": df1["peak_time"].tolist(),
    "start_value": df1["start_value"].tolist(),
    "end_value": df1["end_value"].tolist(),
    "peak_value": df1["peak_value"].tolist(),
    "burst_duration": df1["burst_duration"].tolist(),
    "burst_amplitude": df1["burst_amplitude"].tolist()
}

print(json.dumps(result))
# print(df1)