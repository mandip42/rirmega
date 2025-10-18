
#!/usr/bin/env python3
import os, json, argparse
from pathlib import Path
import numpy as np, pandas as pd, soundfile as sf
C_SOUND=343.0
def load_metadata(ds_dir: Path): return json.loads((ds_dir/"metadata.json").read_text())
def smooth_abs(x, win=5):
    xa = np.abs(x).astype(np.float64); 
    if win<=1: return xa
    k=np.ones(win)/win; return np.convolve(xa,k,mode="same")
def expected_arrival_samples(src, mic, fs):
    dist=float(np.linalg.norm(np.array(mic)-np.array(src))); return int(round(dist/C_SOUND*fs))
def find_direct_index(x, fs, exp_idx, search_ms=5.0, prominence_db=15.0):
    w=int(max(1, round(search_ms*1e-3*fs))); lo=max(0,exp_idx-w); hi=min(len(x), exp_idx+w+1)
    wv = smooth_abs(x[lo:hi], win=7); 
    if len(wv)==0: return exp_idx, False
    peak_val=float(np.max(wv)); 
    if peak_val<=0: return exp_idx, False
    thr = peak_val/(10**(prominence_db/20.0)); candidates=np.where(wv>=thr)[0]
    if len(candidates)==0: return int(np.argmax(wv))+lo, False
    di=int(candidates[np.argmin(np.abs(candidates+lo-exp_idx))]+lo); return di, True
def rt60_schroeder(rir, fs):
    e=rir**2; edc=np.flip(np.cumsum(np.flip(e))); edc=edc/(edc[0]+1e-12); edc_db=10*np.log10(edc+1e-12)
    i1=int(np.argmin(np.abs(edc_db+5))); i2=int(np.argmin(np.abs(edc_db+35)))
    if i2<=i1+1: return 0.0
    x=np.arange(i1,i2)/fs; y=edc_db[i1:i2]; m,_=np.linalg.lstsq(np.vstack([x,np.ones_like(x)]).T,y,rcond=None)[0]
    return float(-60.0/m) if m<0 else 0.0
def smart_join(ds_dir: Path, wav_field: str)->Path:
    p=Path(wav_field)
    if p.is_absolute(): return p
    cand=ds_dir/p
    if cand.exists(): return cand
    cand2 = ds_dir/p.name
    if cand2.exists(): return cand2
    for split in ["train","val","test"]:
        cand3 = ds_dir/split/"wavs"/p.name
        if cand3.exists(): return cand3
    return cand
def validate_item(ds_dir: Path, rec: dict, tol_ms: float=4.0):
    res={"id":rec.get("id","?"),"ok":True,"problems":[]}; fs=int(rec.get("fs",16000))
    src=rec.get("source",[0,0,0]); mics=rec.get("array",{}).get("mics",[]); wav_path=smart_join(ds_dir, rec["wav"])
    if not wav_path.exists(): res["ok"]=False; res["problems"].append(f"wav_missing:{wav_path}"); return res
    audio, fs_file = sf.read(str(wav_path), always_2d=True); 
    if fs_file!=fs: res["ok"]=False; res["problems"].append(f"fs_mismatch:{fs_file}!={fs}")
    peak=float(np.max(np.abs(audio))); 
    if peak>1.0+1e-6: res["ok"]=False; res["problems"].append("clipping")
    tol_samples=max(4, int(tol_ms*1e-3*fs)); errs=[]; flags=[]
    for j, mic in enumerate(mics):
        exp_idx=expected_arrival_samples(src, mic, fs); di, conf = find_direct_index(audio[:,j], fs, exp_idx)
        err=di-exp_idx; errs.append(err); 
        if abs(err)>tol_samples: res["ok"]=False; res["problems"].append(f"arrival_mismatch_max:{abs(err)}")
        if not conf: flags.append(f"low_confidence_ch{j}")
    if flags: res["problems"].extend(flags)
    if errs: res["arrival_err_mean"]=float(np.mean(errs)); res["arrival_err_max"]=int(np.max(np.abs(errs)))
    rt60_meta=float(rec.get("metrics",{}).get("rt60",0.0)); rt60_audio=rt60_schroeder(audio[:,0], fs)
    if rt60_meta>0 and abs(rt60_audio-rt60_meta)>0.35: res["ok"]=False; res["problems"].append("rt60_mismatch")
    return res
def validate_dataset(ds_dir: str, out_csv: str, limit: int|None=None):
    ds_path=Path(ds_dir); recs=load_metadata(ds_path); 
    if limit is not None: recs=recs[:limit]
    rows=[]
    for rec in recs:
        try: rows.append(validate_item(ds_path, rec))
        except Exception as e: rows.append({"id":rec.get("id","?"),"ok":False,"problems":[f"exception:{type(e).__name__}:{e}"]})
    df=pd.DataFrame(rows); df.to_csv(out_csv, index=False)
    ok_rate=100.0*float(df["ok"].mean()) if len(df) else 0.0; print(f"Checked {len(df)} items → {ok_rate:.1f}% passed")
    probs=df["problems"].explode().value_counts().head(10); 
    if len(probs): print("Top issues:"); print(probs)
    else: print("No issues detected."); 
    return df
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--dataset", required=True); ap.add_argument("--report", default="rir_validation_report.csv"); ap.add_argument("--limit", type=int, default=None)
    args=ap.parse_args(); validate_dataset(args.dataset, args.report, args.limit)
