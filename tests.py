import unittest

import steamspypi

import list_daily_releases
import main


class TestListDailyReleasesMethods(unittest.TestCase):
    def test_main(self):
        steamspypi.load()

        assert list_daily_releases.main()


class TestMainMethods(unittest.TestCase):
    def test_main(self):
        assert main.main(no_display_available=True)


if __name__ == '__main__':
    unittest.main()
