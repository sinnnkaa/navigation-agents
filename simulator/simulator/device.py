"""Виртуальный пользователь (§15 ТЗ): идёт по графу улиц и шлёт события в API.

Сегодняшняя версия — один пользователь, только auto_detection-события
движения. Пропуски, ложные срабатывания, обрывы связи и офлайн-очередь —
следующая итерация (полноценный симулятор нагрузки).
"""

import asyncio
import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

import httpx
import networkx as nx

from simulator.graph import bearing_deg, haversine_m

GPS_NOISE_M = 15.0  # §15 ТЗ: ошибки координат — GPS в городе до 15 м


@dataclass
class VirtualDevice:
    device_id: str
    token: str
    graph: nx.Graph
    base_url: str
    rng: random.Random = field(default_factory=random.Random)

    def _random_walk_nodes(self) -> list:
        nodes = list(self.graph.nodes)
        start, end = self.rng.sample(nodes, 2)
        return nx.shortest_path(self.graph, start, end, weight="weight")

    def _noisy_location(self, lat: float, lon: float) -> tuple[float, float, float]:
        accuracy_m = self.rng.uniform(3.0, GPS_NOISE_M)
        dlat, dlon = accuracy_m / 111_320.0, accuracy_m / 111_320.0
        return lat + self.rng.uniform(-dlat, dlat), lon + self.rng.uniform(-dlon, dlon), accuracy_m

    def _build_event(self, lat: float, lon: float, heading: float) -> dict:
        noisy_lat, noisy_lon, accuracy_m = self._noisy_location(lat, lon)
        return {
            "client_event_id": str(uuid.uuid4()),
            "device_id": self.device_id,
            "kind": "auto_detection",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "location": {
                "lat": noisy_lat,
                "lon": noisy_lon,
                "accuracy_m": round(accuracy_m, 1),
                "heading": round(heading, 1),
            },
            "detections": [],
            "media": {},
            "battery": self.rng.randint(20, 100),
            "offline_queued": False,
        }

    async def run(self, client: httpx.AsyncClient, steps: int, interval_s: float = 1.0) -> None:
        path = self._random_walk_nodes()
        headers = {"Authorization": f"Bearer {self.token}"}

        for i in range(min(steps, len(path) - 1)):
            a, b = self.graph.nodes[path[i]], self.graph.nodes[path[i + 1]]
            heading = bearing_deg(a["lat"], a["lon"], b["lat"], b["lon"])
            event = self._build_event(a["lat"], a["lon"], heading)

            response = await client.post(
                f"{self.base_url}/api/v1/events",
                json={"events": [event]},
                headers=headers,
            )
            response.raise_for_status()
            result = response.json()["results"][0]

            distance = haversine_m(a["lat"], a["lon"], b["lat"], b["lon"])
            print(
                f"[{self.device_id}] шаг {i + 1}/{len(path) - 1}: "
                f"событие {result['id']} (дубликат={result['duplicate']}), "
                f"до следующей точки {distance:.0f} м"
            )

            if i < min(steps, len(path) - 1) - 1:
                await asyncio.sleep(interval_s)
