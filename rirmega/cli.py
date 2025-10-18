import argparse
import sys

def cmd_generate(args):
    print(f"[stub] generate → out={args.out} n={args.n} array={args.array} seed={args.seed}")

def main():
    p = argparse.ArgumentParser(prog="rirmega", description="RIR-Mega CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate synthetic RIRs")
    g.add_argument("--out", required=True)
    g.add_argument("--n", type=int, required=True)
    g.add_argument("--array", choices=["linear8","circular8","linear6"], required=True)
    g.add_argument("--seed", type=int, default=0)
    g.set_defaults(func=cmd_generate)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    sys.exit(main())
