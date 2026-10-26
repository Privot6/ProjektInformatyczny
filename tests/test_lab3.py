import unittest, tempfile
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_data import prepare
ROOT=Path(__file__).resolve().parents[1]
class Lab3(unittest.TestCase):
    def test_valid_and_reproducible(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=(ROOT/'data/raw/gios_syntetyczne.csv',ROOT/'data/raw/open_meteo_syntetyczne.csv',tmp)
            first=prepare(*args); first_bytes=(Path(tmp)/'aerorun_dane.csv').read_bytes()
            second=prepare(*args)
            self.assertGreaterEqual(len(first),48)
            self.assertEqual(first_bytes,(Path(tmp)/'aerorun_dane.csv').read_bytes())
            self.assertEqual(len(first),len(second))
    def test_invalid_weather_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'Powtórzony timestamp'):
                prepare(ROOT/'data/raw/gios_syntetyczne.csv',ROOT/'data/test/open_meteo_bledne.csv',tmp)
            self.assertFalse((Path(tmp)/'aerorun_dane.csv').exists())
if __name__=='__main__': unittest.main()
