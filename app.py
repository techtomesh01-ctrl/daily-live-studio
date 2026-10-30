from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from pathlib import Path
import subprocess, threading, os, re, shutil

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
UPLOADS.mkdir(exist_ok=True)
ALLOWED = {".mp4", ".mkv", ".mov", ".webm", ".m4v"}
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024 * 1024
lock = threading.Lock()
process = None
current_file = None

PAGE = r"""<!doctype html><html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>DAILY LIVE STUDIO</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#090a0f;color:#f7f7fa;font:15px/1.5 Segoe UI,Arial,sans-serif}.wrap{max-width:850px;margin:35px auto;padding:20px}.head{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #292b35;padding-bottom:18px}.brand{font-size:23px;font-weight:900;letter-spacing:1px}.brand span{color:#ff3048}.tag{color:#ff8995;font-size:12px}.panel{background:#13151e;border:1px solid #2a2d39;border-radius:16px;padding:22px;margin-top:20px}h1{font-size:30px;margin:5px 0 10px}p,.muted{color:#aeb0bc}.field{margin:17px 0}label{display:block;font-weight:700;margin-bottom:7px}input{width:100%;padding:13px;border:1px solid #373a48;border-radius:9px;background:#090b11;color:white}input[type=file]{padding:10px}.row{display:flex;gap:10px;flex-wrap:wrap}button{border:0;border-radius:9px;padding:13px 19px;font-weight:800;cursor:pointer}.start{background:#ff3048;color:white}.stop{background:#333744;color:white}.status{padding:12px;border-radius:9px;background:#0a0c12;margin-top:14px}.dot{display:inline-block;width:9px;height:9px;border-radius:50%;background:#777;margin-right:8px}.live{background:#ff3048}.log{white-space:pre-wrap;max-height:180px;overflow:auto;color:#d1d2da;font:12px Consolas,monospace}.small{font-size:12px}.warn{border:1px solid #65333d;background:#1c1015;padding:13px;border-radius:10px;color:#ffd5da}@media(max-width:600px){.wrap{margin:10px auto;padding:14px}.head{align-items:flex-start;gap:8px;flex-direction:column}}</style></head><body><div class="wrap">
<header class="head"><div class="brand">DAILY LIVE <span>STUDIO</span></div><div class="tag">LOCAL PC STREAMER · FREE MODE</div></header>
<section class="panel"><h1>YouTube Live Control</h1><p>Video upload karein, YouTube RTMPS details daalein aur Start Live dabayein.</p>
<div class="field"><label>1. Video file select karein</label><input id="video" type="file" accept=".mp4,.mkv,.mov,.webm,.m4v"><div class="muted small" id="fileinfo">MP4 / MKV / MOV / WebM supported</div><div class="status"><b id="uploadstate">Upload abhi shuru nahi hua</b><div style="height:10px;background:#292d39;border-radius:99px;overflow:hidden;margin-top:9px"><div id="uploadbar" style="height:100%;width:0;background:#ff3048"></div></div><div class="muted small" id="uploaddetail">START LIVE dabane par upload shuru hoga.</div></div></div>
<div class="field"><label>2. YouTube RTMPS Server</label><input id="server" value="rtmps://a.rtmps.youtube.com:443/live2" autocomplete="off"></div>
<div class="field"><label>3. YouTube Stream Key (private)</label><input id="key" type="password" placeholder="YouTube Studio se stream key paste karein" autocomplete="new-password"></div>
<div class="warn small">Stream key GitHub par save nahi hoti. Key FFmpeg ke local process arguments mein temporarily aa sakti hai; apna PC account secure rakhein.</div>
<div class="row" style="margin-top:18px"><button class="start" id="start">START LIVE</button><button class="stop" id="stop">STOP LIVE</button></div>
<div class="status"><span class="dot" id="dot"></span><b id="state">Checking...</b><div class="muted small" id="detail"></div></div>
<div class="field"><label>Streaming log</label><div class="log" id="log">Ready.</div></div>
<p class="small">YouTube Studio mein preview check karein. Scheduled stream ho to wahan Go Live dabayein.</p></section>
<p class="muted small">Sirf apne/licensed videos stream karein. PC sleep/off ya internet disconnect hone par stream ruk jayegi.</p></div>
<script>
const $=id=>document.getElementById(id);let uploadedFile=null;
function sizeText(n){return n>=1073741824?(n/1073741824).toFixed(2)+" GB":n>=1048576?(n/1048576).toFixed(1)+" MB":(n/1024).toFixed(1)+" KB";}
$("video").addEventListener("change",()=>{let f=$("video").files[0];uploadedFile=null;$("fileinfo").textContent=f?f.name+" · "+sizeText(f.size):"No file selected";$("uploadstate").textContent=f?"Upload abhi shuru nahi hua":"Upload abhi shuru nahi hua";$("uploadbar").style.width="0%";$("uploaddetail").textContent=f?"START LIVE dabane par "+sizeText(f.size)+" upload hogi.":"Pehle video select karein.";});
function uploadVideo(file){return new Promise((resolve,reject)=>{let fd=new FormData();fd.append("video",file);let x=new XMLHttpRequest();x.open("POST","/api/upload");x.upload.onprogress=e=>{if(e.lengthComputable){let n=Math.round(e.loaded/e.total*100);$("uploadbar").style.width=n+"%";$("uploadstate").textContent="Video upload ho rahi hai: "+n+"%";$("uploaddetail").textContent=sizeText(e.loaded)+" / "+sizeText(e.total);}};x.onload=()=>{let d={};try{d=JSON.parse(x.responseText)}catch{}if(x.status>=200&&x.status<300){$("uploadbar").style.width="100%";$("uploadstate").textContent="UPLOAD COMPLETE ✓";$("uploaddetail").textContent=file.name+" · "+sizeText(file.size)+" · PC ke uploads folder mein save";resolve(d.file);}else reject(Error(d.error||"Upload failed"));};x.onerror=()=>reject(Error("Network error: upload ruk gaya"));x.send(fd);});}
async function refresh(){try{let r=await fetch("/api/status"),d=await r.json();$("state").textContent=d.running?"LIVE PROCESS RUNNING":"NOT STREAMING";$("dot").className="dot"+(d.running?" live":"");$("detail").textContent=d.file?("Video: "+d.file):"";$("log").textContent=d.log||"Ready.";}catch(e){$("state").textContent="Local app not responding";}}
$("start").onclick=async()=>{let f=$("video").files[0];if(!f){alert("Pehle video file select karein.");return}if(!$("key").value.trim()){alert("YouTube stream key daalein.");return}$("start").disabled=true;try{if(!uploadedFile){$("uploadstate").textContent="Upload shuru ho raha hai...";uploadedFile=await uploadVideo(f);} $("state").textContent="YouTube Live shuru ho rahi hai...";let r=await fetch("/api/start",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({file:uploadedFile,server:$("server").value.trim(),key:$("key").value.trim()})}),d=await r.json();if(!r.ok)throw Error(d.error||"Could not start");$("key").value="";await refresh();}catch(e){$("uploadstate").textContent=uploadedFile?"Upload complete; Live start nahi hui":"UPLOAD FAILED";$("uploaddetail").textContent=e.message;alert(e.message);$("key").value="";}finally{$("start").disabled=false;refresh();}};
$("stop").onclick=async()=>{await fetch("/api/stop",{method:"POST"});$("key").value="";refresh();};refresh();setInterval(refresh,2500);
</script></body></html>"""

def ffmpeg_path():
    return shutil.which("ffmpeg")

def is_running():
    return process is not None and process.poll() is None

@app.get("/")
def home():
    return render_template_string(PAGE)

@app.get("/api/status")
def status():
    global process
    with lock:
        running = is_running()
        if process is not None and not running:
            process = None
        try:
            lines = (BASE / "stream.log").read_text(encoding="utf-8", errors="replace").splitlines()[-12:]
            safe_log = "\n".join(lines)
        except Exception:
            safe_log = ""
        return jsonify(running=running, file=current_file if running else None, log=safe_log)

@app.post("/api/upload")
def upload():
    f = request.files.get("video")
    if not f or not f.filename:
        return jsonify(error="Video file missing"), 400
    name = secure_filename(f.filename)
    ext = Path(name).suffix.lower()
    if ext not in ALLOWED:
        return jsonify(error="Unsupported video format"), 400
    target = UPLOADS / name
    if target.exists():
        target = UPLOADS / (Path(name).stem + "_" + str(os.getpid()) + ext)
    f.save(target)
    return jsonify(file=target.name)

@app.post("/api/start")
def start():
    global process, current_file
    data = request.get_json(silent=True) or {}
    filename = str(data.get("file", ""))
    server = str(data.get("server", "")).strip()
    key = str(data.get("key", "")).strip()
    if not filename or Path(filename).name != filename:
        return jsonify(error="Invalid video selection"), 400
    video = (UPLOADS / filename).resolve()
    if UPLOADS.resolve() not in video.parents or not video.is_file():
        return jsonify(error="Uploaded video not found"), 404
    if not ffmpeg_path():
        return jsonify(error="FFmpeg install nahi hai. README-HI.md follow karein."), 400
    if not re.fullmatch(r"rtmps?://[A-Za-z0-9.-]+(?::[0-9]{1,5})?/[A-Za-z0-9_./-]+", server):
        return jsonify(error="RTMP/RTMPS server URL sahi nahi hai"), 400
    host = re.sub(r"^rtmps?://", "", server).split("/")[0].split(":")[0].lower()
    if not (host == "youtube.com" or host.endswith(".youtube.com")):
        return jsonify(error="Security ke liye sirf YouTube ingest server allowed hai"), 400
    if not key or len(key) > 200 or not re.fullmatch(r"[A-Za-z0-9_-]+", key):
        return jsonify(error="Stream key format sahi nahi hai"), 400
    with lock:
        if is_running():
            return jsonify(error="Streaming already running"), 409
        log_file = open(BASE / "stream.log", "w", encoding="utf-8")
        cmd = [ffmpeg_path(), "-hide_banner", "-nostats", "-loglevel", "warning",
               "-re", "-stream_loop", "-1", "-i", str(video),
               "-map", "0:v:0", "-map", "0:a?",
               "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p",
               "-r", "30", "-g", "60", "-b:v", "4500k", "-maxrate", "4500k",
               "-bufsize", "9000k", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
               "-f", "flv", server.rstrip("/") + "/" + key]
        try:
            process = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=log_file,
                stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            current_file = filename
        except Exception as e:
            log_file.close()
            return jsonify(error="FFmpeg start error: " + str(e)), 500
    return jsonify(started=True)

@app.post("/api/stop")
def stop():
    global process, current_file
    with lock:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=3)
        process = None
        current_file = None
    return jsonify(stopped=True)

if __name__ == "__main__":
    print("DAILY LIVE STUDIO: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
