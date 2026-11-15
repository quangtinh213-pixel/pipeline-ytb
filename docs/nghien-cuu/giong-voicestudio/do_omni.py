"""Đo OmniVoice trực tiếp: một tiến trình, T luồng, gom B câu mỗi lô.
Dùng: python do_omni.py --threads 8 --batch 4 --cau cau.txt --out thu_muc --ten nhan [--chi 0,2,4]
In JSON một dòng: thời gian nạp, thời gian tạo, tổng giây tiếng."""
import argparse, json, os, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("--threads", type=int, required=True)
ap.add_argument("--batch", type=int, default=1)
ap.add_argument("--cau", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--ten", required=True)
ap.add_argument("--chi", default="")  # chỉ số câu tiến trình này làm
ap.add_argument("--steps", type=int, default=16)
ap.add_argument("--int8", action="store_true")
ap.add_argument("--wps", type=float, default=0)  # >0: ép thời lượng = số từ / wps
a = ap.parse_args()

for k in ("OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[k] = str(a.threads)
os.environ.setdefault("HF_HUB_CACHE", r"C:\Users\78\AppData\Local\OmniVoice\hf_cache")
os.environ["HF_HUB_OFFLINE"] = "1"

t0 = time.time()
import torch
torch.set_num_threads(a.threads)
torch.set_num_interop_threads(1)
import wave
from omnivoice.models.omnivoice import OmniVoice

model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cpu", dtype=torch.float32)
if a.int8:  # lượng tử hoá động int8 cho các lớp Linear của LLM + đầu ra (fbgemm, AVX2)
    from torch.ao.quantization import quantize_dynamic
    model.llm = quantize_dynamic(model.llm, {torch.nn.Linear}, dtype=torch.qint8)
    model.audio_heads = quantize_dynamic(torch.nn.Sequential(model.audio_heads), {torch.nn.Linear}, dtype=torch.qint8)[0]
REF = r"C:\Users\78\AppData\Roaming\OmniVoice\voices\4751c1f6.wav"
REF_TEXT = open(os.path.join(os.path.dirname(__file__), "ref_text.txt"), encoding="utf-8").read().strip()
prompt = model.create_voice_clone_prompt(REF, ref_text=REF_TEXT)
t_nap = time.time() - t0

cau = [l.strip() for l in open(a.cau, encoding="utf-8") if l.strip()]
idx = [int(x) for x in a.chi.split(",")] if a.chi else list(range(len(cau)))
os.makedirs(a.out, exist_ok=True)
t1, tong, lo = time.time(), 0.0, []
for s in range(0, len(idx), a.batch):
    nhom = idx[s:s + a.batch]
    tb = time.time()
    auds = model.generate(text=[cau[i] for i in nhom], language="vi", voice_clone_prompt=[prompt] * len(nhom),
                          instruct=["male, middle-aged, low pitch"] * len(nhom), num_step=a.steps,
                          guidance_scale=2.0, seed=42,
                          duration=[len(cau[i].split()) / a.wps for i in nhom] if a.wps else None)
    for i, w in zip(nhom, auds):
        pcm = (w.detach().cpu().float().clamp(-1, 1).squeeze(0).numpy() * 32767).astype("int16")
        with wave.open(os.path.join(a.out, f"{a.ten}-c{i}.wav"), "wb") as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(24000); f.writeframes(pcm.tobytes())
        tong += w.shape[-1] / 24000
    lo.append(round(time.time() - tb, 1))
t_tao = time.time() - t1
print(json.dumps({"ten": a.ten, "threads": a.threads, "batch": a.batch, "wps": a.wps, "so_cau": len(idx), "nap_s": round(t_nap, 1),
                  "tao_s": round(t_tao, 1), "tieng_s": round(tong, 1), "he_so": round(t_tao / tong, 2), "lo_s": lo}),
      flush=True)
