# DAILY LIVE STUDIO — Windows PC version

Ye free PC companion aapke computer se selected video ko YouTube Live par continuously loop karta hai. Public GitHub Pages website sirf information/setup page hai; actual streaming local PC app karti hai.

## Zaroori cheezein
- Windows 10/11 PC
- Python 3.10 ya newer
- FFmpeg (PATH mein)
- Stable internet
- YouTube channel par Live streaming enabled
- Video ko broadcast karne ke rights/permission

## 1) Python install karein
https://www.python.org/downloads/ se Python install karein. Installer mein "Add Python to PATH" tick karein.

## 2) FFmpeg install karein
1. https://www.gyan.dev/ffmpeg/builds/ kholein.
2. FFmpeg release essentials ZIP download karein.
3. ZIP extract karke bin folder ka path copy karein (example: C:\ffmpeg\bin).
4. Windows Start mein "Edit the system environment variables" search karein.
5. Environment Variables → User variables → Path → Edit → New → C:\ffmpeg\bin add karein.
6. OK sab jagah. Naya Command Prompt kholkar ffmpeg -version chalayein. Version dikhe to ready.

## 3) Project download karein
GitHub repository: https://github.com/techtomesh01-ctrl/daily-live-studio
Code → Download ZIP → Extract All.

## 4) App start karein
Extracted folder mein START.bat par double-click karein. Pehli baar Python packages install honge. Browser mein http://127.0.0.1:5000 khulega.

## 5) YouTube stream key lein
1. https://studio.youtube.com/ kholein.
2. Create → Go Live.
3. Stream settings mein Stream URL / Server aur Stream key dekhein.
4. Server URL app mein paste karein; default YouTube RTMPS server pehle se diya hai.
5. Stream key password box mein paste karein. Kisi ko share na karein.

## 6) Start karein
1. Video select karein (MP4/MKV/MOV/WebM/M4V).
2. Start Live dabayein.
3. YouTube Studio Live Control Room mein preview check karein.
4. Scheduled stream ho to YouTube Studio mein Go Live dabayein.

Stop Live dabane par FFmpeg band ho jayega. App close karne ya PC sleep/off hone par streaming ruk jayegi.

## Important security
- Stream key ko GitHub, public website, screenshot, chat, ya kisi public jagah par paste na karein.
- App 127.0.0.1 par bind hoti hai, internet par public server nahi banati.
- Key disk/database mein save nahi hoti; streaming ke dauran local FFmpeg process arguments mein temporarily dikh sakti hai. Apna PC account secure rakhein.
- uploads/ aur stream.log local PC par rehte hain; Git ignore rules unhe repository mein upload nahi karte.
- Sirf apne ya licensed videos stream karein.
- Free PC mode 24/7 cloud service nahi hai. PC, app, power aur internet ON rehna zaroori hai.

## Troubleshooting
- FFmpeg missing: FFmpeg bin folder PATH mein add karein, Command Prompt dobara kholein, ffmpeg -version check karein.
- Address already in use: port 5000 busy hai; pehle se chal rahi DAILY LIVE STUDIO window band karein.
- YouTube par offline: stream key/server dobara check karein, YouTube Live enabled status aur internet verify karein.
- Video no audio: source video mein audio track nahi ho sakta; video phir bhi stream ho sakta hai.
- Default upload limit 20 GB hai.
