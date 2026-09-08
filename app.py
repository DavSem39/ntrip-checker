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

        mountpoints = []

        for line in data.decode(
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

            error=(
                "Invalid hostname.\n\n"
                "DNS lookup failed."
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

    # Faster timeout
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
                # RTCM 3.x preamble
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
                f"Connection timed out on port "
                f"{d['port']}.\n\n"
                "Possible causes:\n"
                "- Wrong port number\n"
                "- Firewall blocking traffic\n"
                "- Caster offline\n"
                "- Network connectivity issue"
            )

        )

    except ConnectionRefusedError:

        return jsonify(

            success=False,

            status="OFFLINE",

            error=(
                f"Port {d['port']} is closed.\n\n"
                "No NTRIP service is accepting "
                "connections on this port."
            )

        )

    except socket.gaierror:

        return jsonify(

            success=False,

            status="OFFLINE",

            error=(
                "Invalid hostname.\n\n"
                "DNS lookup failed."
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
