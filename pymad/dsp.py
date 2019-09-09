from math import floor, ceil, pi, log2
from .core import sequence
import numpy as np

fft = np.fft.fft
ifft = np.fft.ifft

def repeat2(x, ratio, step=32, win_ratio=32):
    "change length but keep pitch"
    n = x.shape[0]
    mm = ceil(ratio * n)
    fs = x.fs
    win_len = ceil(step * win_ratio)

    seg = max(0, ceil((n - win_len) / step))
    step2 = max(0, ceil((mm - win_len) / seg))
    step_ratio = step2 / step

    amp = np.sqrt(np.sum(x * x) / n)
    x = np.pad(x, ((0, win_len + seg * step - n)), mode='constant')

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
        syns = np.real(ifft(fq))

        st1 = i * step2
        ed1 = st1 + win_len
        out[st1:ed1] += syns
    
    amp1 = np.sqrt(np.sum(out * out) / m)
    out = out / amp1 * amp
    return sequence(out[:mm], fs)

def boxSmooth(x, w):
    box = np.ones(w, dtype=np.float32) / w
    return np.convolve(x, box, mode='same')

def preservePeak(x, thres=0):
    "preserve only local max, x must be non-negative, also suppress < thres * max_x"
    max_x = np.max(x)
    x = x * (x > thres * max_x)
    x_pad = np.pad(x, 1, mode='edge')
    x = x * (x > x_pad[2:]) * (x > x_pad[:-2])
    return x

def findPitch(x, thres=0.1, eps=1e-6, min_freq=50):
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
    sy = preservePeak(sy, thres=thres)
    sy = np.log(sy + eps)
    # cepstrum
    sy = np.abs(ifft(sy))
    sy = preservePeak(sy)
    return sy

def nextPow2(n):
    return int(2 ** ceil(log2(n)))

def pad_to(x, n):
    return np.pad(x, ((0, n - x.shape[0])), mode='constant')

def resample2(x, ratio):
    "change both length and pitch"
    fs = x.fs
    n = x.shape[0]
    nn = nextPow2(n)
    x = pad_to(x, nn)
    fq = fft(x)

    m = ceil(n * ratio)
    mm = nextPow2(m)
    fq1 = np.zeros(mm, dtype=np.complex)

    n1 = nn // 2 + 1
    m1 = mm // 2 + 1
    tp = np.arange(n1) / nn
    xp = fq[:n1]
    t = np.arange(m1) / mm * ratio
    fq1[:m1] = ratio * np.interp(t, tp, xp, right=0)
    fq1[m1:mm] = np.conj(fq1[(mm - m1):0:-1])

    o = np.real(ifft(fq1))
    return sequence(o[:m], fs)

def filter4(x, pitch, ratio=4, max_freq=5000):
    "a comb filter, also a low pass filter to cut at max_freq"
    fs = x.fs
    n = x.shape[0]
    nn = nextPow2(n)
    n1 = nn // 2 + 1
    x = pad_to(x, nn)

    idx = pitch / fs * nn
    tt = np.arange(n1) / idx
    tr = np.maximum(1, np.round(tt))
    tr = np.minimum(ceil(max_freq / pitch), tr)
    tt -= tr
    tt = np.maximum(0, 1 - (tt * ratio) ** 2)

    tt = pad_to(tt, nn)
    tt[n1:nn] = np.conj(tt[(nn - n1):0:-1])

    o = np.real(ifft(tt * fft(x)))
    return sequence(o[:n], fs)
