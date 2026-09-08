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
def mps():

    data = request.json

    sock = socket.socket()

    sock.settimeout(10)

    try:

        sock.connect(
            (
                data["host"],
                int(data["port"])
            )
        )

        sock.sendall(

            auth(

                data["host"],
                data["port"],
                data["username"],
                data["password"]

            ).encode()

        )

        text = b""

        while True:

            chunk = sock.recv(4096)

            if not chunk:
                break

            text += chunk

        mountpoints = []

        for line in text.decode(
            errors="ignore"
        ).splitlines():

            if line.startswith("STR;"):

                mountpoints.append(

                    line.split(";")[1]

                )

        return jsonify(

            success=True,

            mountpoints=mountpoints

        )

    except Exception as e:

        return jsonify(

            success=False,

            error=str(e)

        )

    finally:

        sock.close()


@app.post("/test_connection")
def test_connection():

    data = request.json

    sock = socket.socket()

    sock.settimeout(5)

    try:

        start = time.time()

        sock.connect(

            (
                data["host"],
                int(data["port"])
            )

        )

        latency = round(

            (time.time() - start)

            * 1000

        )

        sock.sendall(

            auth(

                data["host"],
                data["port"],
                data["username"],
                data["password"],
                f"/{data['mountpoint']}"

            ).encode()

        )

        end_time = time.time() + 5

        bytes_received = 0

        rtcm_detected = False

        while time.time() < end_time:

            try:

                packet = sock.recv(4096)

                if not packet:
                    break

                bytes_received += len(packet)

                if b"\xD3" in packet:

                    rtcm_detected = True

            except:

                break

        if rtcm_detected:

            status = "ONLINE"

        else:

            status = "NO RTCM DATA"

        return jsonify(

            success=True,

            status=status,

            latency_ms=latency,

            bytes_received=bytes_received,

            rtcm_detected=rtcm_detected

        )

    except Exception as e:

        return jsonify(

            success=False,

            status="OFFLINE",

            error=str(e)

        )

    finally:

        sock.close()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000
    )
