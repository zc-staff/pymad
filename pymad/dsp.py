from math import floor, ceil, pi
from .core import sequence
import numpy as np

fft = np.fft.fft
ifft = np.fft.ifft

def repeat2(x, ratio, step=32, win_ratio=32):
    "change length but keep pitch"
    step_ratio = ratio

    fs = x.fs
    win_len = ceil(step * win_ratio)
    step2 = ceil(step * step_ratio)
    step_ratio = step2 / step
    n = x.shape[0]
    amp = np.sqrt(np.sum(x * x) / n)
    seg = max(0, ceil((n - win_len) / step))
    x = np.concatenate((x, np.zeros(win_len + seg * step - n)))

    m = win_len + seg * step2
    out = np.zeros(m)
    win = np.hamming(win_len)

    now = win * x[0:win_len]
    out[0:win_len] = win * now
    unwrap = 2 * pi * step * np.arange(win_len, dtype=np.float32) / win_len
    phase = np.angle(fft(now))
    phase1 = np.copy(phase)

    for i in range(1, seg + 1):
        st = i * step
        ed = st + win_len
        now = win * x[st:ed]

        f = fft(now)
        fq = np.abs(f)
        phase0 = phase
        phase = np.angle(f)

        delta = (phase - phase0) - unwrap
        delta -= np.round(delta / (2 * pi)) * (2 * pi)
        delta = (delta + unwrap) * step_ratio

        phase1 += delta
        fq = fq * np.exp(1j * phase1)
        syns = win * np.real(ifft(fq))

        st1 = i * step2
        ed1 = st1 + win_len
        out[st1:ed1] += syns
    
    amp1 = np.sqrt(np.sum(out * out) / m)
    out = out / amp1 * amp
    mm = round(n * step_ratio)
    return sequence(out[:mm], fs)

def box_smooth(x, w):
    box = np.ones(w, dtype=np.float32) / w
    return np.convolve(x, box, mode='same')

def preserve_peak(x, thres=0):
    "preserve only local max, x must be non-negative, also suppress < thres * max_x"
    max_x = np.max(x)
    x = x * (x > thres * max_x)
    x_pad = np.pad(x, 1, mode='edge')
    x = x * (x > x_pad[2:]) * (x > x_pad[:-2])
    return x

def find_pitch(x, thres=0.1, eps=1e-6, min_freq=50):
    "pitch finding using cepstrum method"
    fs = x.fs
    n = x.shape[0]
    max_n = ceil(fs / min_freq)
    cp = cepstrum(x, thres, eps)
    k = np.argmax(cp[:max_n])
    if k > n / 2:
        k = n - k
    return float(fs / k)

def cepstrum(x, thres=0.1, eps=1e-6):
    # mag spectrum
    sy = np.abs(fft(x))
    sy = preserve_peak(sy, thres=thres)
    sy = np.log(sy + eps)
    # cepstrum
    sy = np.abs(ifft(sy))
    sy = preserve_peak(sy)
    return sy

def resample2(x, ratio):
    "change both length and pitch"
    fs = x.fs
    n = x.shape[0]
    t = floor((n - 1) / 2)
    t1 = ceil(t * ratio)
    fq = fft(x)
    fq1 = np.zeros(2 * t1 + 1, dtype=np.complex)
    fq1[0] = fq[0] * ratio

    tt = min(t, t1)
    fq1[1:(1 + tt)] = fq[1:(1 + tt)] * ratio
    fq1[(2 * t1):t1:-1] = np.conj(fq1[1:(1 + t1)])

    o = np.real(ifft(fq1))
    return sequence(o, fs)

def filter4(x, pitch, ratio=4, max_freq=5000):
    "a comb filter, also a low pass filter to cut at max_freq"
    fs = x.fs
    n = x.shape[0]
    t = ceil((n + 1) / 2)

    idx = pitch / fs * n
    tt = np.arange(1, t) / idx
    tr = np.maximum(1, np.round(tt))
    tr = np.minimum(ceil(max_freq / pitch), tr)
    tt -= tr
    tt = np.maximum(0, 1 - (tt * ratio) ** 2)

    f1 = np.zeros(n)
    f1[1:t] = tt
    f1[t:n] = np.conj(f1[(n - t):0:-1])

    f0 = fft(x)
    return sequence(np.real(ifft(f0 * f1)), fs)

