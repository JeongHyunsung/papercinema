import glob, re, numpy as np, soundfile as sf, script, os, json
from asr import transcribe
import librosa
L = {l["id"]: l for l in script.LINES}
ref = " ".join(L[i]["sub"] for i in ["L01","L08","L11","L16","L17"])
norm = lambda s: re.sub(r"[^a-z' ]"," ",s.lower().replace("0.9","zero point nine").replace("2.53","two point five three").replace("segen","see jen").replace("b-flex","bee flex").replace("-"," ")).split()
def wer(r,h):
    d=np.arange(len(h)+1)
    for i,x in enumerate(r,1):
        p=d.copy(); d[0]=i
        for j,y in enumerate(h,1): d[j]=min(p[j]+1,d[j-1]+1,p[j-1]+(x!=y))
    return d[-1]/len(r)
R=norm(ref); out={}
for f in sorted(glob.glob("casting/*.wav")):
    v=os.path.basename(f)[:-4]; a,sr=sf.read(f,dtype="float32")
    txt,_,_=transcribe(a,sr); H=norm(txt)
    f0,vf,_=librosa.pyin(librosa.resample(a,orig_sr=sr,target_sr=16000),fmin=60,fmax=400,sr=16000,frame_length=1024)
    f0=f0[vf]; st=12*np.log2(f0/np.median(f0))
    rms=librosa.feature.rms(y=a,frame_length=1024,hop_length=240)[0]; sil=(rms<.1*np.median(rms)).mean()
    out[v]=dict(dur=round(len(a)/sr,1),wpm=round(len(R)/(len(a)/sr)*60),wer=round(wer(R,H),3),
               f0_med=round(float(np.median(f0))),pitch_iqr_st=round(float(np.subtract(*np.percentile(st,[90,10]))),1),
               pause=round(float(sil),2),hyp=txt.lower())
    print(v,{k:x for k,x in out[v].items() if k!="hyp"})
json.dump(out,open("casting/metrics.json","w"),indent=1)
