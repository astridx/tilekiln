from unittest import TestCase

from tilekiln.tile import Tile


class TestConfig(TestCase):
    def test_properties(self):
        t = Tile(3, 2, 1)
        self.assertEqual(t.zoom, 3)
        self.assertEqual(t.x, 2)
        self.assertEqual(t.y, 1)

    def test_bounds(self):
        t = Tile(3, 2, 1)
        self.assertEqual(t.bbox(0), 'ST_TileEnvelope(3, 2, 1, margin=>0)')
        self.assertEqual(t.bbox(8/4096), 'ST_TileEnvelope(3, 2, 1, margin=>0.001953125)')

    def test_eq(self):
        t1 = Tile(3, 2, 1)
        t2 = Tile(3, 2, 1)
        t3 = Tile(3, 1, 1)

        self.assertEqual(t1, t2)
        self.assertNotEqual(t1, t3)

    def test_tileid(self):
        self.assertEqual(Tile(0, 0, 0).tileid, 0)
        self.assertEqual(Tile(0, 0, 0), Tile.from_tileid(0))
        self.assertEqual(Tile(1, 0, 0).tileid, 1)
        self.assertEqual(Tile(1, 0, 0), Tile.from_tileid(1))
        self.assertEqual(Tile(2, 0, 0).tileid, 5)
        self.assertEqual(Tile(2, 0, 0), Tile.from_tileid(5))
        self.assertEqual(Tile(2, 1, 0).tileid, 6)
        self.assertEqual(Tile(2, 1, 0), Tile.from_tileid(6))
