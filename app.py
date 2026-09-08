import socket
import time
import base64

from flask import Flask, render_template, request, jsonify


app = Flask(__name__)


def auth(host, port, username, password, path="/"):

    encoded = base64.b64encode(
        f"{username}:{password}".encode()
    ).decode()

    return (
        f"GET {path} HTTP/1.0\r\n"
        f"Authorization: Basic {encoded}\r\n"
        f"User-Agent: NTRIPChecker\r\n"
        f"\r\n"
    )


@app.route("/")
def home():

    return render_template("index.html")


@app.post("/mountpoints")
def mountpoints():

    d = request.json

    s = socket.socket()
    s.settimeout(10)

    try:

        host = d["host"]
        port = int(d["port"])

        s.connect((host, port))

        s.sendall(

            auth(
                host,
                port,
                d["username"],
                d["password"]
            ).encode()

        )

        data = b""

        while True:

            chunk = s.recv(4096)

            if not chunk:
                break

            data += chunk

        text = data.decode(
            errors="ignore"
        )

        mountpoints = []

        for line in text.splitlines():

            if line.startswith("STR;"):

                try:

                    mountpoints.append(
                        line.split(";")[1]
                    )

                except:
                    pass

        return jsonify(

            success=True,

            mountpoints=mountpoints

        )

    except socket.timeout:

        return jsonify(

            success=False,

            error=(
                "Connection timed out.\n\n"
                "Possible causes:\n"
                "- Wrong port\n"
                "- Firewall blocking traffic\n"
                "- Caster offline"
            )

        )

    except ConnectionRefusedError:

        return jsonify(

            success=False,

            error=(
                f"Port {d['port']} is closed.\n\n"
                "No NTRIP service is listening."
            )

        )

    except socket.gaierror:

        return jsonify(

            success=False,

            error="Invalid hostname."

        )

    except Exception as e:

        return jsonify(

            success=False,

            error=str(e)

        )

    finally:

        s.close()


@app.post("/test_connection")
def test_connection():

    d = request.json

    s = socket.socket()

    s.settimeout(3)

    try:

        host = d["host"]
        port = int(d["port"])
        username = d["username"]
        password = d["password"]
        mountpoint = d["mountpoint"]

        start_time = time.time()

        s.connect((host, port))

        latency_ms = round(
            (time.time() - start_time) * 1000
        )

        s.sendall(

            auth(
                host,
               
