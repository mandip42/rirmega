<<<<<<< HEAD
# RIR-Mega v1.2.1

Synthetic Room Impulse Responses with tools for generation, validation, visualization, HF-style loading, and a baseline dereverb demo.

- **Dataset (Zenodo DOI):** https://doi.org/10.5281/zenodo.17387402  
- **Hugging Face dataset:** https://huggingface.co/datasets/mandipgoswami/rirmega
- **Paper (arXiv):** https://arxiv.org/abs/2510.18917


# RIR-Mega v1.2.1

This package builds synthetic **Room Impulse Responses** and includes tools for validation, visualization, HF-style loading, and a baseline dereverb demo.

## Install
```bash
pip install -e .
# Ensure pyroomacoustics is new enough for WPE (optional for baseline):
pip install --upgrade pyroomacoustics
```

## Generate
```bash
rirmega generate --out ./rir_output_50k --n 50000 --array linear8
rirmega generate --out ./rir_output_8k_circ --n 8000 --array circular8 --seed 1000

```

## HF-style preview
```bash
python scripts/hf_loader.py --dataset ./rir_output --head 5
```

## Baseline demo (convolve + optional WPE)
```bash
# Option A: use your own clean mono 16 kHz file
python scripts/baseline_dereverb.py --dataset ./rir_output_1k --speech ./clean.wav --out demo_out

# Option B: create a small placeholder
python scripts/baseline_dereverb.py --dataset ./rir_output_1k --make-dummy --out demo_out
```
Outputs:
- `demo_out/reverb_multich.wav`
- `demo_out/dereverb_wpe_ch0.wav` (if WPE available; otherwise a fallback)
- Console prints **SI-SDR** for reverbed vs dereverbed vs dry.

## Visualization + Validation (Mini Set of 1000 rooms)
```bash
python scripts/rir_visual_check.py --dataset ./rir_output_1k
python scripts/rir_validation_v3.py --dataset ./rir_output_1k --report ./rir_validation_report.csv
```
## Visualization + Validation (Full Set)
```bash
python scripts/rir_visual_check.py --dataset ./rir_output_50k
python scripts/rir_validation_v3.py --dataset ./rir_output_50k --report ./rir_validation_report.csv
```
=======
## Citation
Please cite both the paper and the dataset
```bash
@misc{goswami2025rirmega,
  title        = {RIR-Mega: A Large-Scale Room Impulse Response Corpus with Benchmarks for Industrial and Building Acoustics},
  author       = {Goswami, Mandip},
  year         = {2025},
  eprint       = {2510.18917},
  archivePrefix= {arXiv},
  primaryClass = {cs.SD},
  url          = {https://arxiv.org/abs/2510.18917}
}

@dataset{goswami_2025_rirmega_zenodo,
  author       = {Goswami, Mandip},
  title        = {RIR-Mega Dataset},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {v1.0.0},
  doi          = {10.5281/zenodo.17387402},
  url          = {https://doi.org/10.5281/zenodo.17387402}
}
```
```bash
Goswami, M. (2025). RIR-Mega: A Large-Scale Room Impulse Response Corpus with Benchmarks for Industrial and Building Acoustics. arXiv:2510.18917. https://arxiv.org/abs/2510.18917

Goswami, M. (2025). RIR-Mega Dataset (v1.0.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.17387402
```
# rirmega
>>>>>>> f50426243d870c1d43846b60c0efff81917818ce

