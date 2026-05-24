import io
import json
import urllib.parse
import unittest
from unittest.mock import MagicMock, patch

import distance


class DistanceTests(unittest.TestCase):
    @staticmethod
    def _mock_response(payload: str):
        response = MagicMock()
        response.__enter__.return_value = io.StringIO(payload)
        response.__exit__.return_value = None
        return response

    def test_haversine_zero_for_same_point(self):
        self.assertAlmostEqual(distance.haversine_km((10.0, 20.0), (10.0, 20.0)), 0.0, places=7)

    def test_geocode_address_returns_lat_lon(self):
        payload = [{"lat": "12.34", "lon": "56.78"}]

        with patch("urllib.request.urlopen", return_value=self._mock_response(json.dumps(payload))) as mock_urlopen:
            lat, lon = distance.geocode_address("test")

        request = mock_urlopen.call_args.args[0]
        self.assertIn("DragonDistance/1.0", request.headers["User-agent"])
        query_params = urllib.parse.parse_qs(urllib.parse.urlparse(request.full_url).query)
        self.assertEqual(query_params["q"], ["test"])
        self.assertEqual(query_params["format"], ["json"])
        self.assertEqual(query_params["limit"], ["1"])
        self.assertEqual((lat, lon), (12.34, 56.78))

    def test_geocode_address_raises_when_no_results(self):
        with patch("urllib.request.urlopen", return_value=self._mock_response("[]")):
            with self.assertRaises(distance.AddressLookupError):
                distance.geocode_address("missing")

    def test_geocode_address_rejects_empty_input(self):
        with self.assertRaises(distance.AddressLookupError):
            distance.geocode_address("   ")

    def test_haversine_non_zero_distance(self):
        result = distance.haversine_km((40.7128, -74.0060), (42.3601, -71.0589))
        self.assertAlmostEqual(result, 306.11, places=1)

    def test_calculate_distance_km_integrates_lookup_and_distance(self):
        with patch("distance.geocode_address", side_effect=[(0.0, 0.0), (0.0, 1.0)]) as geocode:
            km = distance.calculate_distance_km("A", "B")

        self.assertAlmostEqual(km, 111.19, places=2)
        geocode.assert_any_call("A")
        geocode.assert_any_call("B")


if __name__ == "__main__":
    unittest.main()
