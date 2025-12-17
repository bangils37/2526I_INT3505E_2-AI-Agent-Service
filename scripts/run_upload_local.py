import asyncio
from pathlib import Path
from unittest.mock import AsyncMock
import sys

# Ensure project root is on sys.path so `src` can be imported when running this script directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.services.retrieval_client import RetrievalClient

PATH = Path(r'D:\Tài liệu Kỳ 1 2025-2026\2526I_INT3505E_2-AI-Agent-Service-Retrieval\mock\documents\document-001.jsonl')

if not PATH.exists():
    print(f"File not found: {PATH}")
    raise SystemExit(1)

data = PATH.read_bytes()
filename = PATH.name

import argparse
import logging

parser = argparse.ArgumentParser(description="Upload a local document to the Retrieval service (default http://localhost:8010)")
parser.add_argument("path", nargs="?", default=str(PATH), help="Path to the JSONL file to upload")
parser.add_argument("--collection", default="document_001", help="Collection name to upload to")
parser.add_argument("--doc-id", dest="document_id", default="document_001", help="Document ID")
parser.add_argument("--mock", action="store_true", help="Mock network calls instead of performing real HTTP requests")
parser.add_argument("--yes", "-y", action="store_true", help="Assume yes to any prompts")
args = parser.parse_args()

# If a different path was passed on the command line, override
if args.path and args.path != str(PATH):
    PATH = Path(args.path)
    if not PATH.exists():
        print(f"File not found: {PATH}")
        raise SystemExit(1)
    data = PATH.read_bytes()
    filename = PATH.name

logging.basicConfig(level=logging.INFO)
client = RetrievalClient()

# Optionally patch lower-level methods to avoid making network calls during this run
if args.mock:
    client.upload_document = AsyncMock(return_value={"success": True, "document_id": args.document_id, "collection": args.collection})
    client.check_exists_document = AsyncMock(return_value={"exists": True, "document_id": args.document_id, "collection": args.collection})
    client.index_document = AsyncMock(return_value={"success": True, "document_id": args.document_id, "collection": args.collection, "logs": []})

async def run():
    print(f"About to upload {filename} -> collection='{args.collection}' document_id='{args.document_id}' to {client.base_url}")
    if not args.yes:
        confirm = input("Proceed? [y/N]: ")
        if confirm.lower() not in ("y", "yes"):
            print("Aborted")
            return

    try:
        res = await client.upload_document_full_flow(args.collection, args.document_id, file=data, filename=filename)
        print("Result:\n", res)
    except Exception as e:
        print("Upload failed:", repr(e))
    finally:
        # Close the underlying httpx client if it exists
        try:
            await client._client.aclose()
        except Exception:
            pass

if __name__ == '__main__':
    asyncio.run(run())
