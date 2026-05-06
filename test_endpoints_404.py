import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_result(name, url, method, status, response_text):
    color = "\033[92m" if status in [200, 201, 404] else "\033[91m"
    reset = "\033[0m"
    print(f"[{method}] {name:<35} URL: {url:<45} -> {color}Status: {status}{reset}")
    if status not in [200, 201]:
        try:
            parsed = json.loads(response_text)
            print(f"   Error: {parsed}")
        except:
            pass

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
    print("--- Probando peticiones de detalle (IDs inexistentes - Deberían dar 404) ---")
    detail_endpoints = [
        {"name": "Medicamentos Detalle GET", "url": f"{BASE_URL}/medicamentos/9999/", "method": "GET"},
        {"name": "Tratamientos Detalle GET", "url": f"{BASE_URL}/tratamientos/00000000-0000-0000-0000-000000000000/", "method": "GET"},
        {"name": "Paciente Tratamiento Detalle GET", "url": f"{BASE_URL}/paciente-tratamiento/9999/", "method": "GET"},
        {"name": "Tratamiento Medicamento Detalle GET", "url": f"{BASE_URL}/tratamiento-medicamento/9999/", "method": "GET"},
    ]

    for ep in detail_endpoints:
        status, text = make_request(ep["url"], ep["method"])
        print_result(ep["name"], ep["url"], ep["method"], status, text)

if __name__ == '__main__':
    test_endpoints()
