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

    d = request.json

    s = socket.socket()

    s.settimeout(10)

    try:

        s.connect(
            (
                d["host"],
                int(d["port"])
            )
        )

        s.sendall(

            auth(

                d["host"],
                d["port"],
                d["username"],
                d["password"]

            ).encode()

        )

        txt = b""

        while True:

            x = s.recv(4096)

            if not x:
                break

            txt += x

        mountpoints = []

        for line in txt.decode(
            errors="ignore"
        ).splitlines():

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

    s.settimeout(5)

    try:

        start = time.time()

        s.connect(

            (
                d["host"],
                int(d["port"])
            )

        )

        latency = round(

            (time.time() - start)

            * 1000

        )

        s.sendall(

            auth(

                d["host"],
                d["port"],
                d["username"],
                d["password"],
                f"/{d['mountpoint']}"

            ).encode()

        )

        end = time.time() + 5

        bytes_received = 0

        rtcm_detected = False

        while time.time() < end:

            try:

                packet = s.recv(4096)

                if not packet:
                    break

                bytes_received += len(packet)

                # RTCM v3 preamble
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

        s.close()


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
