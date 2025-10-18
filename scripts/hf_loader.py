
#!/usr/bin/env python3
import os, json, argparse, pandas as pd
def load_local(dataset_dir):
    with open(os.path.join(dataset_dir, "metadata.json"), "r") as f:
        for rec in json.load(f):
            yield rec
if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--head", type=int, default=5)
    args=ap.parse_args()
    rows=[]
    for i,ex in enumerate(load_local(args.dataset)):
        rows.append({
            "id": ex.get("id"),
            "family": ex.get("family","NA"),
            "split": ex.get("split","NA"),
            "fs": ex.get("fs","NA"),
            "wav": ex.get("wav"),
            "rt60": ex.get("metrics",{}).get("rt60","NA"),
            "drr_db": ex.get("metrics",{}).get("drr_db","NA"),
        })
        if i+1 >= max(args.head, 1): break
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
