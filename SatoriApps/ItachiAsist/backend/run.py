#!/usr/bin/env python3
"""
SATORI ECOSYSTEM — ItachiAssist Backend
========================================
run.py — Serverni ishga tushirish skripti

Ishlatish:
    python3 run.py
    python3 run.py --reload        # Dev rejim (hot-reload)
    python3 run.py --host 0.0.0.0  # Tashqi kirish
    python3 run.py --port 8765
"""

import argparse
import sys
from pathlib import Path

# app/ papkasini path ga qo'shish
sys.path.insert(0, str(Path(__file__).parent))


def parse_args():
    parser = argparse.ArgumentParser(description="Satori ItachiAssist Backend")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--reload", action="store_true", help="Hot-reload (dev)")
    parser.add_argument("--workers", type=int, default=1)
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        import uvicorn
    except ImportError:
        print("❌ uvicorn o'rnatilmagan. O'rnatish:")
        print("   pip install uvicorn[standard]")
        sys.exit(1)

    print(f"\n🌌 Satori ItachiAssist Backend")
    print(f"📍 http://{args.host}:{args.port}")
    print(f"📚 Docs: http://{args.host}:{args.port}/docs")
    print(f"🔄 Reload: {args.reload}\n")

    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=1 if args.reload else args.workers,
        log_level="info",
    )


if __name__ == "__main__":
    main()
