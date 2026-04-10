from flask import Flask, request

app = Flask(__name__)

def parse_non_negative_int(value: str):
    if value is None:
        return None
    value = value.strip()
    if not value.isdigit():
        return None
    return int(value)

def lcm(x: int, y: int) -> int:
    if x == 0 or y == 0:
        return 0

    a, b = x, y
    while b:
        a, b = b, a % b
    gcd = a
    return (x * y) // gcd

@app.get("/yigit_kaya12_mail_srv_com")
def get_lcm():
    x = parse_non_negative_int(request.args.get("x"))
    y = parse_non_negative_int(request.args.get("y"))

    if x is None or y is None:
        return "NaN", 200, {"Content-Type": "text/plain; charset=utf-8"}

    return str(lcm(x, y)), 200, {"Content-Type": "text/plain; charset=utf-8"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)