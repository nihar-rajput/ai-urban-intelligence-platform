from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class GPSPoint:
    lat: float
    lon: float
    time_offset: float  # seconds from start


class SimulatedGPSEngine:
    """
    Interpolates bus location along realistic predefined urban routes based on video timestamps.
    Explicitly flags all coordinates as SIMULATED GPS to maintain transparency.
    """

    # Pre-configured bus routes in New Delhi
    ROUTES: Dict[str, List[GPSPoint]] = {
        "BUS-001": [
            GPSPoint(lat=28.6315, lon=77.2167, time_offset=0.0),    # Connaught Place Outer Circle
            GPSPoint(lat=28.6250, lon=77.2185, time_offset=15.0),   # Janpath
            GPSPoint(lat=28.6129, lon=77.2295, time_offset=30.0),   # India Gate
            GPSPoint(lat=28.5910, lon=77.2240, time_offset=45.0),   # Lodhi Road
            GPSPoint(lat=28.5672, lon=77.2100, time_offset=60.0),   # AIIMS New Delhi
        ],
        "BUS-002": [
            GPSPoint(lat=28.5494, lon=77.2534, time_offset=0.0),    # Nehru Place Terminal
            GPSPoint(lat=28.5412, lon=77.2580, time_offset=20.0),   # Kalkaji Mandir
            GPSPoint(lat=28.5700, lon=77.2370, time_offset=40.0),   # Lajpat Nagar Ring Road
            GPSPoint(lat=28.5750, lon=77.2150, time_offset=60.0),   # South Extension
        ],
        "BUS-003": [
            GPSPoint(lat=28.6562, lon=77.2410, time_offset=0.0),    # Red Fort / Netaji Subhash Marg
            GPSPoint(lat=28.6510, lon=77.2300, time_offset=20.0),   # Chandni Chowk
            GPSPoint(lat=28.6675, lon=77.2280, time_offset=40.0),   # ISBT Kashmere Gate
            GPSPoint(lat=28.6810, lon=77.2200, time_offset=60.0),   # Civil Lines
        ]
    }

    @classmethod
    def get_position(cls, bus_id: str, timestamp_sec: float) -> Tuple[float, float, float]:
        """
        Interpolates (latitude, longitude, speed_kmh) for a given bus at a given relative timestamp.
        Returns a tuple: (latitude, longitude, speed_kmh).
        """
        route = cls.ROUTES.get(bus_id, cls.ROUTES["BUS-001"])
        if not route:
            return 28.6139, 77.2090, 32.0

        max_time = route[-1].time_offset
        # Loop route smoothly if video exceeds max_time
        t_mod = timestamp_sec % max_time if max_time > 0 else 0.0

        # Find enclosing waypoint segment
        p1 = route[0]
        p2 = route[-1]
        for i in range(len(route) - 1):
            if route[i].time_offset <= t_mod <= route[i + 1].time_offset:
                p1 = route[i]
                p2 = route[i + 1]
                break

        segment_duration = p2.time_offset - p1.time_offset
        if segment_duration <= 0:
            fraction = 0.0
        else:
            fraction = (t_mod - p1.time_offset) / segment_duration

        lat = p1.lat + (p2.lat - p1.lat) * fraction
        lon = p1.lon + (p2.lon - p1.lon) * fraction
        speed_kmh = 30.0 + (fraction * 15.0)  # Simulated speed ~ 30-45 km/h

        return round(lat, 6), round(lon, 6), round(speed_kmh, 1)


gps_simulator = SimulatedGPSEngine()
