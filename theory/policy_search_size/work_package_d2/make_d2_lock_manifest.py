from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "D2_LOCK_MANIFEST.json"
TRACKED = [
    "D2_THEORY_MEMO.md", "d2_core.py", "D2_RUNTIME_PREFLIGHT.py", "D2_PREFLIGHT_CONFIG.json",
    "D2_NUMERICAL_PROTOCOL.md", "D2_NUMERICAL_CONFIG.json", "D2_NUMERICAL_CONFIG_SMOKE.json",
    "d2_validation_core.py", "d2_validate.py", "run_preflight.sh",
    "run_d2_validation_smoke.sh", "run_d2_validation_full.sh",
    "make_d2_lock_manifest.py", "verify_d2_lock_manifest.py", "references.bib",
    "README.md", "README_NUMERICAL.md", ".gitignore",
    "tests/test_d2_core.py", "tests/test_d2_numerical.py",
]
def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()
def main() -> None:
    records=[]
    for rel in TRACKED:
        path=ROOT/rel
        if not path.is_file():
            raise FileNotFoundError(f"Required D2 lock file not found: {rel}")
        records.append({"file":rel,"size_bytes":path.stat().st_size,"sha256":sha256(path)})
    payload={"study_id":"TESS_THEORY_D2_NUMERICAL_VALIDATION_V1","status":"locked_before_run","required_lock_tag":"tess-theory-work-package-d2-v1-lock-20260802","files":records}
    OUTPUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(f"D2 lock manifest written: {OUTPUT}")
    print(f"Files hashed: {len(records)}")
if __name__=='__main__': main()
