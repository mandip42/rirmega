
#!/usr/bin/env python3
import os, json, argparse, numpy as np, soundfile as sf, librosa
from scipy.signal import fftconvolve
def si_sdr(reference, estimate, eps=1e-9):
    r = reference - np.mean(reference); e = estimate - np.mean(estimate)
    s_target = np.dot(e, r) / (np.dot(r, r) + eps) * r; e_noise = e - s_target
    return 10*np.log10((np.sum(s_target**2)+eps)/(np.sum(e_noise**2)+eps))
def convolve_multichannel(x, R):  # x mono, R (T,M)
    return np.stack([fftconvolve(x, R[:,m], mode="full") for m in range(R.shape[1])], axis=1)
def make_dummy(sr=16000, dur_s=8.0, seed=0):
    t = np.arange(int(sr*dur_s))/sr; rng = np.random.default_rng(seed); x = rng.standard_normal(t.shape[0])
    X = np.fft.rfft(x); freqs = np.fft.rfftfreq(len(x), 1/sr); band = (freqs>=300)&(freqs<=3400); X *= band.astype(float)
    x_band = np.fft.irfft(X, n=len(x)); env = 0.5*(1+np.sin(2*np.pi*2.0*t))*0.4 + 0.6; return 0.2 * x_band * env, sr
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True); ap.add_argument("--speech", default=None)
    ap.add_argument("--idx", type=int, default=0); ap.add_argument("--out", default="demo_out")
    ap.add_argument("--make-dummy", action="store_true", help="Generate a placeholder speech-like signal if no --speech")
    args = ap.parse_args(); os.makedirs(args.out, exist_ok=True)
    items = json.load(open(os.path.join(args.dataset, "metadata.json")))
    rec = items[min(max(args.idx,0), len(items)-1)]
    rir_path = os.path.join(args.dataset, rec["wav"]); R, fs = sf.read(rir_path, always_2d=True)  # (T,M)
    # Load/prepare speech
    if args.speech is None and args.make_dummy:
        s, sr = make_dummy(sr=fs)
    elif args.speech is not None:
        s, sr = librosa.load(args.speech, sr=fs, mono=True)
    else:
        raise SystemExit("Provide --speech <file.wav> or use --make-dummy")
    # Convolve
    y = convolve_multichannel(s, R); sf.write(os.path.join(args.out, "reverb_multich.wav"), y, fs)
    # Try WPE
    try:
        from pyroomacoustics.dereverberation import wpe
        Y = wpe(y.T, taps=10, delay=3, iterations=3)  # (M,N) in, (M,N) out
        y_wpe = Y.T[:,0]
        method = "WPE"
    except Exception as e:
        print(f"WPE unavailable ({e}); falling back to channel 0 passthrough.")
        y_wpe = y[:,0]
        method = "passthrough"
    sf.write(os.path.join(args.out, "dereverb_wpe_ch0.wav"), y_wpe, fs)
    # Scores
    L = min(len(s), len(y_wpe)); s_ = s[:L]; y0_ = y[:L,0]; y_wpe_ = y_wpe[:L]
    print("SI-SDR reverb_ch0:", si_sdr(s_, y0_))
    print(f"SI-SDR {method}_ch0:", si_sdr(s_, y_wpe_))
if __name__ == "__main__":
    main()
