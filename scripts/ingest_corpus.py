import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import argparse
from src.extensions.rag.ingester import ingest, CORPUS_DIR, DB_PATH

parser = argparse.ArgumentParser(description="Ingest corpus into LanceDB")
parser.add_argument("--corpus-dir", type=Path, default=CORPUS_DIR)
parser.add_argument("--db-path", type=str, default=DB_PATH)
parser.add_argument("--reset", action="store_true", help="Drop and re-create the table")
args = parser.parse_args()

ingest(corpus_dir=args.corpus_dir, db_path=args.db_path, reset=args.reset)
