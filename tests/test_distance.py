import io
import json
import unittest
from unittest.mock import patch

import distance


class DistanceTests(unittest.TestCase):
    def test_haversine_zero_for_same_point(self):
        self.assertAlmostEqual(distance.haversine_km((10.0, 20.0), (10.0, 20.0)), 0.0, places=7)

    def test_geocode_address_returns_lat_lon(self):
        payload = [{"lat": "12.34", "lon": "56.78"}]

        with patch("urllib.request.urlopen", return_value=io.StringIO(json.dumps(payload))):
            lat, lon = distance.geocode_address("test")

        self.assertEqual((lat, lon), (12.34, 56.78))

    def test_geocode_address_raises_when_no_results(self):
        with patch("urllib.request.urlopen", return_value=io.StringIO("[]")):
            with self.assertRaises(distance.AddressLookupError):
                distance.geocode_address("missing")


if __name__ == "__main__":
    unittest.main()
