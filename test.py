import logging

try:
    from run import app
    import unittest

except Exception as ex:
    logging.critical(f"Some modules are missing. Please install and try again. {ex}")


class FlaskTest(unittest.TestCase):

    # Check for response code 200
    def test_index(self):
        tester = app.test_client(self)
        response = tester.get("/")
        self.assertEqual(response.status_code, 200)

    # Check if response is JSON
    def test_index_content_type(self):
        tester = app.test_client(self)
        response = tester.get("/")
        self.assertIn("application/json", response.content_type)


if __name__ == "__main__":
    unittest.main()
