import unittest

import download_json
import list_daily_releases
import main


class TestDownloadJsonMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(download_json.main())


class TestListDailyReleasesMethods(unittest.TestCase):

    def test_main(self):
        download_json.main()

        self.assertTrue(list_daily_releases.main())


class TestMainMethods(unittest.TestCase):

    def test_main(self):
        self.assertTrue(main.main(no_display_available=True))


if __name__ == '__main__':
    unittest.main()
