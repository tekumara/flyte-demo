import math
from typing import Generator, Tuple

# Semi-axes of WGS-84 geoidal reference
WGS84_a = 6378137.0  # Major semiaxis [m]
WGS84_b = 6356752.3  # Minor semiaxis [m]


class Position:
    def __init__(self, lat: float, long: float):
        self.lat = lat
        self.long = long

    def validate(self) -> None:
        if self.lat < -90 or self.lat > 90:
            raise ValueError("Bad latitude given ({})".format(self.lat))

        if self.long < -180 or self.long > 180:
            raise ValueError("Bad longitude given ({})".format(self.long))


# Bounding box surrounding the point at given coordinates,
# assuming local approximation of Earth surface as a sphere
# of radius given by WGS84
def bounding_box(position: Position, radius_km: float) -> "Area":
    lat = deg2rad(degrees=position.lat)
    lon = deg2rad(degrees=position.long)
    half_side = 1000 * radius_km

    # Radius of Earth at given latitude
    radius = wgs84_earth_radius(lat=lat)
    # Radius of the parallel at given latitude
    pradius = radius * math.cos(lat)

    lat_min = lat - half_side / radius
    lat_max = lat + half_side / radius
    lon_min = lon - half_side / pradius
    lon_max = lon + half_side / pradius

    return Area(
        point1=Position(rad2deg(lat_min), rad2deg(lon_min)),
        point2=Position(rad2deg(lat_max), rad2deg(lon_max)),
    )


class Area:
    def __init__(self, point1: Position, point2: Position):
        self.point1 = point1
        self.point2 = point2

    def validate(self) -> None:
        for point in self.points:
            point.validate()

    @property
    def points(self) -> Tuple[Position, Position]:
        return (self.point1, self.point2)

    @property
    def lats(self) -> Generator[float, None, None]:
        return (point.lat for point in self.points)

    @property
    def longs(self) -> Generator[float, None, None]:
        return (point.long for point in self.points)

    @property
    def bounding_box(self) -> Tuple[float, float, float, float]:
        return (min(self.lats), max(self.lats), min(self.longs), max(self.longs))


# degrees to radians
def deg2rad(degrees: float) -> float:
    return math.pi * degrees / 180.0


# radians to degrees
def rad2deg(radians: float) -> float:
    return 180.0 * radians / math.pi


# Earth radius at a given latitude, according to the WGS-84 ellipsoid [m]
def wgs84_earth_radius(lat: float) -> float:
    an = WGS84_a * WGS84_a * math.cos(lat)
    bn = WGS84_b * WGS84_b * math.sin(lat)
    ad = WGS84_a * math.cos(lat)
    bd = WGS84_b * math.sin(lat)
    return math.sqrt((an * an + bn * bn) / (ad * ad + bd * bd))
