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

    # Check if the response of the job_status api is application/json
    def test_index_content_type(self):
        tester = app.test_client(self)
        response = tester.get("/job_status")
        self.assertIn("application/json", response.content_type)

     # Check if the response of the build_push_image api is HTML
    def test_content_type(self):
        tester = app.test_client(self)
        response = tester.get("/build_push_image")
        self.assertIn("text/html", response.content_type)


    # Check for Data returned from the job_status api   
    def test_index_data(self):
        tester = app.test_client(self)
        response = tester.get("/job_status")
        self.assertTrue(b"message" in response.data)


if __name__ == "__main__":
    unittest.main()
