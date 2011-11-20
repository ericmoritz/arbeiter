import unittest
from arbeiter import Arbeiter


class TestArbeiter(unittest.TestCase):

    def test_arbeiter(self):

        def myarbeiter(a, data):
            newdata = data.lower()
            return {"lowercase-strings": newdata}
        
        # Set up the arbeiter to read data from the "in" queue
        a = Arbeiter(["localhost:22133"], "in", myarbeiter)

        # Flush all values out of it's work queue
        a.flush()

        # Push a value into the "in" queue
        a.push("Test")
        
        # Tell the arbeiter to handle the next item in it's queue
        a.handle_one()

        # Wait for the value to come out of the lowercase-string queue
        result = a.get("lowercase-strings", timeout=5000,
                       durable=False)
        
        # Assert that everything worked
        self.assertEqual(result, "test")


