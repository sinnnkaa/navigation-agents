"""Граф улиц для симулятора (§15 ТЗ).

Сегодняшняя версия — синтетическая сетка вместо реального графа OSM:
Overpass API недоступен из текущего окружения (сетевая изоляция песочницы
блокирует overpass-api.de). Интерфейс намеренно узкий (Graph = networkx.Graph
с атрибутами узлов lat/lon), чтобы заменить build_demo_graph на загрузку
через osmnx.graph_from_place(...) без изменений в остальном симуляторе.
"""

import math

import networkx as nx

EARTH_RADIUS_M = 6_371_000.0


def _meters_to_latlon_delta(dx_m: float, dy_m: float, at_lat_deg: float) -> tuple[float, float]:
    dlat = dy_m / 111_320.0
    dlon = dx_m / (111_320.0 * math.cos(math.radians(at_lat_deg)))
    return dlat, dlon


def build_demo_graph(
    rows: int = 4,
    cols: int = 4,
    spacing_m: float = 80.0,
    origin: tuple[float, float] = (55.7512, 37.6178),
) -> nx.Graph:
    """Сетка rows x cols, узлы связаны с соседями по горизонтали/вертикали."""
    origin_lat, origin_lon = origin
    graph = nx.Graph()

    for r in range(rows):
        for c in range(cols):
            dlat, dlon = _meters_to_latlon_delta(c * spacing_m, r * spacing_m, origin_lat)
            graph.add_node((r, c), lat=origin_lat + dlat, lon=origin_lon + dlon)

    for r in range(rows):
        for c in range(cols):
            if c + 1 < cols:
                graph.add_edge((r, c), (r, c + 1), weight=spacing_m)
            if r + 1 < rows:
                graph.add_edge((r, c), (r + 1, c), weight=spacing_m)

    return graph


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def bearing_deg(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dlambda = math.radians(lon2 - lon1)
    x = math.sin(dlambda) * math.cos(p2)
    y = math.cos(p1) * math.sin(p2) - math.sin(p1) * math.cos(p2) * math.cos(dlambda)
    return (math.degrees(math.atan2(x, y)) + 360) % 360
