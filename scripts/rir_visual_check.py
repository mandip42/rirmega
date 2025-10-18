
#!/usr/bin/env python3
import os, json, argparse, random, numpy as np, pandas as pd, soundfile as sf, matplotlib.pyplot as plt
C_SOUND = 343.0
def load_metadata(ds_dir): return json.load(open(os.path.join(ds_dir,"metadata.json")))
def smart_join(ds_dir, wav_field):
    p=os.path.join(ds_dir, wav_field)
    if os.path.exists(p): return p
    base=os.path.basename(wav_field)
    for split in ["train","val","test"]:
        cand=os.path.join(ds_dir, split, "wavs", base)
        if os.path.exists(cand): return cand
    return os.path.join(ds_dir, base)
def expected_arrival_samples(src, mic, fs):
    dist = np.linalg.norm(np.array(mic)-np.array(src)); return int(round(dist / C_SOUND * fs))
def rt60_schroeder(rir, fs):
    e = rir**2; edc=(np.flip(np.cumsum(np.flip(e))))/(np.sum(e)+1e-12)
    edc_db = 10*np.log10(edc+1e-12); i1=int(np.argmin(np.abs(edc_db+5))); i2=int(np.argmin(np.abs(edc_db+35)))
    if i2<=i1+1: return 0.0, edc_db
    x=np.arange(i1,i2)/fs; y=edc_db[i1:i2]; m,_=np.linalg.lstsq(np.vstack([x,np.ones_like(x)]).T,y,rcond=None)[0]
    return float(-60/m) if m<0 else 0.0, edc_db
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--dataset", required=True); ap.add_argument("--sample", type=int, default=None); args=ap.parse_args()
    recs = load_metadata(args.dataset); df=pd.DataFrame(recs); sizes=pd.DataFrame(df["room_size"].to_list(), columns=["Lx","Ly","Lz"]); sizes["Volume"]=sizes.prod(axis=1)
    rt60s = df["metrics"].apply(lambda m:m.get("rt60",0.0)).astype(float); drrs=df["metrics"].apply(lambda m:m.get("drr_db",0.0)).astype(float)
    idx = args.sample if args.sample is not None else random.randrange(len(recs)); rec=recs[idx]; wav_path=smart_join(args.dataset,rec["wav"])
    x,fs = sf.read(wav_path, always_2d=True); ref=x[:,0]; t=np.arange(len(ref))/fs; exp_idx=expected_arrival_samples(rec["source"], rec["array"]["mics"][0], fs)
    w=int(max(1, round(5.0e-3*fs))); lo=max(0,exp_idx-w); hi=min(len(ref), exp_idx+w+1); di=int(np.argmax(np.abs(ref[lo:hi])))+lo if hi>lo else exp_idx
    rt60_est, edc_db = rt60_schroeder(ref, fs)
    import matplotlib.pyplot as plt
    fig,axs = plt.subplots(3,3,figsize=(14,10))
    axs[0,0].hist(rt60s, bins=30); axs[0,0].set_title("RT60 (metadata)"); axs[0,0].set_xlabel("Seconds"); axs[0,0].set_ylabel("Count")
    axs[0,1].hist(drrs, bins=30); axs[0,1].set_title("DRR (metadata)"); axs[0,1].set_xlabel("dB"); axs[0,1].set_ylabel("Count")
    axs[0,2].hist(sizes["Volume"], bins=30); axs[0,2].set_title("Room Volume"); axs[0,2].set_xlabel("m³"); axs[0,2].set_ylabel("Count")
    axs[1,0].hist(sizes["Lx"], bins=20); axs[1,0].set_title("Lx (m)"); axs[1,1].hist(sizes["Ly"], bins=20); axs[1,1].set_title("Ly (m)"); axs[1,2].hist(sizes["Lz"], bins=20); axs[1,2].set_title("Lz (m)")
    sc=axs[2,0].scatter(sizes["Lx"], sizes["Ly"], c=sizes["Lz"], alpha=0.6); axs[2,0].set_xlabel("Lx (m)"); axs[2,0].set_ylabel("Ly (m)"); axs[2,0].set_title("Length vs Width (color=Height)"); cb=fig.colorbar(sc, ax=axs[2,0]); cb.set_label("Height (m)")
    axs[2,1].plot(t, ref); axs[2,1].axvline(exp_idx/fs, linestyle="--", label="expected"); axs[2,1].axvline(di/fs, linestyle=":", label="detected"); axs[2,1].legend(); axs[2,1].set_title(f"Waveform {rec['id']}")
    axs[2,2].plot(edc_db); axs[2,2].set_title(f"Schroeder EDC, RT60≈{rt60_est:.2f}s"); axs[2,2].set_xlabel("Samples"); axs[2,2].set_ylabel("dB")
    plt.tight_layout(); plt.show()
if __name__=="__main__": main()
