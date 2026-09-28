"""Точка входа симулятора.

Устройство должно быть заранее зарегистрировано в бэкенде:

    cd backend && source .venv/bin/activate && python -m app.scripts.provision_device

Пример запуска:

    python -m simulator.main --device-id <uuid> --token <token> --steps 12
"""

import argparse
import asyncio

import httpx

from simulator.device import VirtualDevice
from simulator.graph import build_demo_graph


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8010")
    parser.add_argument("--device-id", required=True)
    parser.add_argument("--token", required=True)
    parser.add_argument("--steps", type=int, default=10)
    parser.add_argument("--interval", type=float, default=1.0, help="секунд между событиями")
    parser.add_argument("--seed", type=int, default=None, help="§15 ТЗ: детерминированность по seed")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    graph = build_demo_graph()
    device = VirtualDevice(
        device_id=args.device_id,
        token=args.token,
        graph=graph,
        base_url=args.base_url,
    )
    if args.seed is not None:
        device.rng.seed(args.seed)

    async with httpx.AsyncClient(timeout=10.0) as client:
        await device.run(client, steps=args.steps, interval_s=args.interval)


if __name__ == "__main__":
    asyncio.run(main())
