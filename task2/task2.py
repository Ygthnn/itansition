from pathlib import Path
import hashlib
import zipfile
import sys

def sort_key(hex_hash: str) -> int:
    prod = 1
    for ch in hex_hash:
        prod *= (int(ch, 16) + 1)
    return prod

def sha3_256_bytes(data: bytes) -> str:
    return hashlib.sha3_256(data).hexdigest()

def sha3_256_file(path: Path) -> str:
    h = hashlib.sha3_256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def main():
    if len(sys.argv) != 3:
        print("Usage: python task2.py task2.zip your_email@example.com")
        sys.exit(1)

    zip_path = Path(sys.argv[1])
    email = sys.argv[2].strip().lower()

    extract_dir = Path("task2_extracted")
    if extract_dir.exists():
        for p in sorted(extract_dir.rglob("*"), reverse=True):
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                p.rmdir()
    extract_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    files = sorted([p for p in extract_dir.rglob("*") if p.is_file()])

    hashes = [sha3_256_file(p) for p in files]
    hashes.sort(key=sort_key)

    joined = "".join(hashes)
    final_hash = sha3_256_bytes((joined + email).encode("utf-8"))

    print(f"!task2 {email} {final_hash}")

if __name__ == "__main__":
    main()