import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_result(name, url, method, status, response_text):
    color = "\033[92m" if status in [200, 201] else "\033[91m"
    reset = "\033[0m"
    print(f"[{method}] {name:<30} URL: {url:<40} -> {color}Status: {status}{reset}")
    if status not in [200, 201]:
        try:
            parsed = json.loads(response_text)
            print(f"   Error: {parsed}")
        except:
            print(f"   Error: {response_text[:200]}")

def make_request(url, method="GET", data=None):
    req = urllib.request.Request(url, method=method)
    if data is not None:
        req.add_header('Content-Type', 'application/json')
        jsondata = json.dumps(data).encode('utf-8')
        req.data = jsondata
    
    try:
        with urllib.request.urlopen(req) as response:
            return response.status, response.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8')
    except urllib.error.URLError as e:
        return 0, str(e.reason)

def test_endpoints():
    endpoints = [
        {"name": "Medicamentos GET", "url": f"{BASE_URL}/medicamentos/", "method": "GET"},
        {"name": "Tratamientos GET", "url": f"{BASE_URL}/tratamientos/", "method": "GET"},
        {"name": "Paciente Tratamiento GET", "url": f"{BASE_URL}/paciente-tratamiento/", "method": "GET"},
        {"name": "Tratamiento Medicamento GET", "url": f"{BASE_URL}/tratamiento-medicamento/", "method": "GET"},
    ]

    print("--- Probando peticiones GET ---")
    for ep in endpoints:
        status, text = make_request(ep["url"], ep["method"])
        print_result(ep["name"], ep["url"], ep["method"], status, text)

    print("\n--- Probando validaciones POST (Deberia dar 400 Bad Request) ---")
    post_endpoints = [
        {"name": "Medicamentos POST", "url": f"{BASE_URL}/medicamentos/", "method": "POST", "data": {}},
        {"name": "Tratamientos POST", "url": f"{BASE_URL}/tratamientos/", "method": "POST", "data": {}},
        {"name": "Paciente Tratamiento POST", "url": f"{BASE_URL}/paciente-tratamiento/", "method": "POST", "data": {}},
        {"name": "Tratamiento Medicamento POST", "url": f"{BASE_URL}/tratamiento-medicamento/", "method": "POST", "data": {}},
    ]
    for ep in post_endpoints:
        status, text = make_request(ep["url"], ep["method"], ep["data"])
        print_result(ep["name"], ep["url"], ep["method"], status, text)

if __name__ == '__main__':
    test_endpoints()
