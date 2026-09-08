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

        txt = b""

        while True:

            chunk = s.recv(4096)

            if not chunk:
                break

            txt += chunk

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

    except socket.timeout:

        return jsonify(

            success=False,

            error=(
                "Connection timed out. "
                "Check hostname, port or firewall."
            )

        )

    except ConnectionRefusedError:

        return jsonify(

            success=False,

            error=(
                "Connection refused. "
                "No NTRIP service is listening on this port."
            )

        )

    except socket.gaierror:

        return jsonify(

            success=False,

            error=(
                "Invalid hostname "
                "or DNS lookup failed."
            )

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

        host = d["host"]
        port = int(d["port"])
        username = d["username"]
        password = d["password"]
        mountpoint = d["mountpoint"]

        start_time = time.time()

        s.connect((host, port))

        latency_ms = round(

            (time.time() - start_time)

            * 1000

        )

        s.sendall(

            auth(

                host,
                port,
                username,
                password,
                f"/{mountpoint}"

            ).encode()

        )

        finish_time = time.time() + 5

        bytes_received = 0

        rtcm_detected = False

        while time.time() < finish_time:

            try:

                packet = s.recv(4096)

                if not packet:
                    break

                bytes_received += len(packet)

                #
                # RTCM 3.x packets start
                # with preamble 0xD3
                #
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

            latency_ms=latency_ms,

            bytes_received=bytes_received,

            rtcm_detected=rtcm_detected

        )

    except socket.timeout:

        return jsonify(

            success=False,

            status="OFFLINE",

            error=(
                f"Port {d['port']} did not respond. "
                "Possible wrong port, firewall or caster offline."
            )

        )

    except ConnectionRefusedError:

        return jsonify(

            success=False,

            status="OFFLINE",

            error=(
                f"Port {d['port']} is closed. "
                "No service is accepting connections."
            )

        )

    except socket.gaierror:

        return jsonify(

            success=False,

            status="OFFLINE",

            error=(
                "Invalid hostname or DNS lookup failed."
            )

        )

    except Exception as e:

        return jsonify(

            success=False,

            status="OFFLINE",

            error=f"Unexpected error: {str(e)}"

        )

    finally:

        s.close()


if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=False

    )
