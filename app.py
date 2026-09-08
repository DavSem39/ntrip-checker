import socket, base64
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

def get_mountpoints(host, port, username, password):
    enc = base64.b64encode(f'{username}:{password}'.encode()).decode()
    req = f'GET / HTTP/1.0\r\nAuthorization: Basic {enc}\r\nUser-Agent: NTRIPChecker\r\n\r\n'
    s=socket.socket(); s.settimeout(10)
    try:
        s.connect((host,int(port))); s.sendall(req.encode())
        resp=b''
        while True:
            d=s.recv(4096)
            if not d: break
            resp+=d
        m=[]
        for line in resp.decode(errors='ignore').splitlines():
            if line.startswith('STR;'): m.append(line.split(';')[1])
        return {'success':True,'mountpoints':m}
    except Exception as e:
        return {'success':False,'error':str(e)}
    finally:
        s.close()

@app.route('/')
def home(): return render_template('index.html')

@app.route('/mountpoints',methods=['POST'])
def mountpoints():
    return jsonify(get_mountpoints(**request.json))

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)
