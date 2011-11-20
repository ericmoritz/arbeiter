import unittest
from arbeiter import Job


class TestJob(unittest.TestCase):

    def test_arbeiter(self):

        def handler(job, data):
            newdata = data.lower()
            return {"lowercase-strings": newdata}
        
        # Set up the arbeiter to read data from the "in" queue
        job = Job(["localhost:22133"], "in", handler)

        # Flush all values out of it's work queue
        job.flush()

        # Push a value into the "in" queue
        job.push("Test")
        
        # Tell the arbeiter to handle the next item in it's queue
        job.handle_one()

        # Wait for the value to come out of the lowercase-string queue
        result = job.get("lowercase-strings", timeout=5000,
                       durable=False)
        
        # Assert that everything worked
        self.assertEqual(result, "test")

    def test_sink(self):
        results = []

        def handler(job, data):
            data = data.lower()
            results.append(data)

        
        # Set up the arbeiter to read data from the "in" queue
        job = Job(["localhost:22133"], "in", handler)

        # Flush all values out of it's work queue
        job.flush()

        # Push a value into the "in" queue
        job.push("Test")
        
        # Tell the arbeiter to handle the next item in it's queue
        job.handle_one()

        # Assert that everything worked
        self.assertEqual(results[0], "test")
        
        # Ensure the data has been removed from the queue
        self.assertTrue(job.peek("in") is None)

    def test_fail(self):
        class TestException(Exception):
            pass

        def handler(job, data):
            raise TestException("someone set us up the bomb")
        
        # Set up the arbeiter to read data from the "in" queue
        job = Job(["localhost:22133"], "in", handler)

        # Flush all values out of it's work queue
        job.flush()

        # Push a value into the "in" queue
        job.push("Test")
        
        # Tell the arbeiter to handle the next item in it's queue
        self.assertRaises(TestException, job.handle_one)

        # Ensure the data was put back in the queue
        self.assertEqual(job.peek("in"), "Test")
        
