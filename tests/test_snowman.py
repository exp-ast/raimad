import unittest

import pycif as pc

class TestSnowman(unittest.TestCase):

    def test_snowman(self):
        compo = pc.Snowman(nose_length=20, eye_size=2.5)
        geom = compo.get_geoms()

        # Test layers
        self.assertEqual(geom.keys(), {'snow', 'carrot', 'pebble'})

        # Test three circles on snow layer
        self.assertEqual(len(geom['snow']), 3)

        # Test marks
        self.assertTrue('nose' in compo.marks.keys())

        import pathlib
        pathlib.Path('/tmp/tmp.cif').write_text(pc.export_cif(compo))


if __name__ == '__main__':
    unittest.main()

