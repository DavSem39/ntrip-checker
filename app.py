import socket,time,base64
from flask import Flask,render_template,request,jsonify
app=Flask(__name__)

def auth(h,p,u,pw,path='/'):
 e=base64.b64encode(f'{u}:{pw}'.encode()).decode()
 return f'GET {path} HTTP/1.0\r\nAuthorization: Basic {e}\r\nUser-Agent: NTRIPChecker\r\n\r\n'

@app.route('/')
def home(): return render_template('index.html')

@app.post('/mountpoints')
def mps():
 d=request.json;s=socket.socket();s.settimeout(10)
 try:
  s.connect((d['host'],int(d['port'])));s.sendall(auth(d['host'],d['port'],d['username'],d['password']).encode())
  txt=b''
  while True:
   x=s.recv(4096)
   if not x: break
   txt+=x
  m=[]
  for l in txt.decode(errors='ignore').splitlines():
   if l.startswith('STR;'): m.append(l.split(';')[1])
  return jsonify(success=True,mountpoints=m)
 except Exception as e:
  return jsonify(success=False,error=str(e))
 finally:s.close()

@app.post('/test_connection')
def test():
 d=request.json;s=socket.socket();s.settimeout(10)
 try:
  t=time.time();s.connect((d['host'],int(d['port'])));lat=round((time.time()-t)*1000)
  s.sendall(auth(d['host'],d['port'],d['username'],d['password'],f"/{d['mountpoint']}").encode())
  total=0;end=time.time()+5
  while time.time()<end:
   try:
    b=s.recv(4096)
    if b: total+=len(b)
   except: break
  return jsonify(success=True,status='ONLINE' if total>0 else 'NO DATA',bytes_received=total,latency_ms=lat)
 except Exception as e:
  return jsonify(success=False,status='OFFLINE',error=str(e))
 finally:s.close()

if __name__=='__main__': app.run()
