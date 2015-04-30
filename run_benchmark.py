import sys
from app import app

# Init httplib2
import httplib2
h = httplib2.Http(".cache")

# HTTP GET /vin:Winery
url = "%svin:Winery" % app.REST_API_URL
print "GET %s" % url
resp, content = h.request(url, "GET")
print content

# Benchmark
from time import time
start = time()
count = 80
for i in range(count):
    resp, content = h.request(url, "GET")   
    sys.stdout.write(".")
end = time()
print("")
print("BENCHMARK")
print("HTTP GET: %s requests / sec" % (count/(end-start)))
