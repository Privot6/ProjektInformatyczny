"""Odtwórz oba scenariusze w osobnym katalogu i porównaj zapisane pliki."""

from pathlib import Path
from tempfile import TemporaryDirectory

from compare_methods import run, sha256


FILES = ("observations.csv", "comparison.csv", "lab3_application.csv", "run.json")
ROOT = Path(__file__).resolve().parents[1]


def main():
    reference = ROOT / "results/lab4"
    with TemporaryDirectory(prefix="lab4-check-", dir=reference.parent) as temporary:
        reproduced = Path(temporary)
        run(ROOT / "data/raw/lab4", ROOT / "data/processed/sample-clean.json", reproduced)
        for scenario in (Path("."), Path("sensitivity")):
            for name in FILES:
                relative = scenario / name
                expected = sha256(reference / relative)
                actual = sha256(reproduced / relative)
                if actual != expected:
                    raise SystemExit(f"Różnica w {relative}: {actual} zamiast {expected}")
                print(f"{relative}: {actual}")
    print("8 plików zgodnych bajtowo")


if __name__ == "__main__":
    main()
