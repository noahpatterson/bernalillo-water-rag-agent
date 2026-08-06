"""Download ABCWUA CCR (Consumer Confidence Report) PDFs into data/raw/abcwua/.

URLs and local filenames match data/raw/abcwua/SOURCE.txt. PDFs are gitignored;
run this after clone instead of committing the binaries.
"""

from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "data" / "raw" / "abcwua"

# (local filename, upstream URL) — newest report year first
CCR_PDFS: list[tuple[str, str]] = [
    (
        "ABCWUA-CCR-2025.pdf",
        "https://www.abcwua.org/wp-content/uploads/2026/05/ABCWUA-2025WaterQualityMailerWeb.pdf",
    ),
    (
        "ABCWUA-CCR-2024.pdf",
        "https://www.abcwua.org/wp-content/uploads/2025/04/ABCWUA-2024WaterQualityMailerWeb-FINAL2.pdf",
    ),
    (
        "ABCWUA-CCR-2023.pdf",
        "https://www.abcwua.org/wp-content/uploads/2024/04/ABCWUA-2023WaterQualityMailerWeb.pdf",
    ),
    (
        "ABCWUA-CCR-2022.pdf",
        "https://www.abcwua.org/wp-content/uploads/2023/05/2022WaterQualityMailerWeb.pdf",
    ),
    (
        "ABCWUA-CCR-2021.pdf",
        "https://www.abcwua.org/wp-content/uploads/2022/05/ABCWUA-2021WaterQualityReport_Web_FINAL.pdf",
    ),
    (
        "ABCWUA-CCR-2020.pdf",
        "https://www.abcwua.org/wp-content/uploads/2021/05/ABCWUA-2021WaterQualityMailerWeb.pdf",
    ),
]


def download(url: str, dest: Path, force: bool) -> str:
    if dest.exists() and not force:
        return "skip"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "bernalillo-water-rag/0.1 (CCR fetch; local setup)"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())
    return "ok"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="re-download even if the local PDF already exists",
    )
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    failures = 0

    for filename, url in CCR_PDFS:
        dest = OUT_DIR / filename
        try:
            status = download(url, dest, force=args.force)
        except urllib.error.URLError as e:
            print(f"FAIL  {filename}: {e}", file=sys.stderr)
            failures += 1
            continue

        if status == "skip":
            print(f"skip  {dest.relative_to(ROOT)} (exists; use --force to refresh)")
        else:
            print(f"ok    {dest.relative_to(ROOT)}")

    if failures:
        print(f"\n{failures} download(s) failed", file=sys.stderr)
        return 1

    print(f"\nDone. PDFs in {OUT_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
