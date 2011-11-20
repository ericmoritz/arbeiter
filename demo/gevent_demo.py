import gevent
from gevent import monkey; monkey.patch_all()
import requests
from arbeiter import Arbeiter


def handle_message(a, data):
    print "Got: %s" % (data)
    response = requests.post("http://posttestserver.com/post.php",
                             data=data)
    print response



input_queue = Arbeiter(["127.0.0.1:22133"], "in", handle_message)

if __name__ == '__main__':
    g = gevent.spawn(input_queue.run)
    g.join()

