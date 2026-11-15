import json,re,html,unicodedata,sys
N={x['id']:x for x in json.load(open('nguon.json'))}
def txt(f):
  t=open(f,errors='ignore').read(); t=re.sub(r'<script.*?</script>|<style.*?</style>','',t,flags=re.S)
  t=html.unescape(re.sub(r'<[^>]+>',' ',t)); return unicodedata.normalize('NFC',re.sub(r'\s+',' ',t))
src={'nvidianews.nvidia.com/news/nvidia-announces':txt('nguon/nvidia-pr.html'),'sec.gov':txt('nguon/sec-8k.htm'),'conference-call':txt('nguon/nvidia-conference-call.html'),
 'fptcloud':txt('/tmp/video-huang/1c6e0c.html')}
import glob
print('--- trích dẫn nguyên văn')
for i,x in N.items():
  if not x['trich_dan']: continue
  for k,t in src.items():
    if k in x['url']:
      q=unicodedata.normalize('NFC',x['trich_dan'])
      ok = q.replace('’',"'") in t.replace('’',"'")
      print(i,'OK' if ok else 'KHÔNG THẤY')
# script checks
K=open('kich-ban.md').read()
tc=json.load(open('/tmp/pipeline-ytb/pipeline_phong-cach_tu-cam.json'))
low=K.lower()
err=[]
for grp in ['tu','mo_bai','ket_bai','dich_tho']:
  for w in tc[grp]:
    if w in low: err.append(f'Lỗi tu-cam[{grp}]: {w}')
for p in tc['mau']:
  for m in re.finditer(p,low): err.append(f'Lỗi mẫu: {m.group(0)[:60]}')
if re.search(r'\bmình\b',low): err.append('Có chữ "mình": '+str([low[m.start()-30:m.start()+20] for m in re.finditer(r'\bmình\b',low)]))
ids=set(re.findall(r'\[#([a-z0-9]+)\]',K))
miss=ids-set(N); print('--- id thiếu trong nguon:',miss); print('id không dùng:',set(N)-ids)
# loi doc
beats=re.split(r'#### ',K)[1:]; total=0
for b in beats:
  name=b.split('\n')[0]; ld=b.split('**Lời đọc:**')[1]; scr=b.split('**Lời đọc:**')[0]
  paras=[p.strip() for p in ld.strip().split('\n') if p.strip()]
  clean=re.sub(r'\[#[a-z0-9]+\]','',ld)
  w=len(clean.split()); total+=w
  if re.search(r'\d',clean): err.append(f'Chữ số trong lời đọc: {name}: '+str(re.findall(r'.{20}\d.{10}',clean)))
  for p in paras:
    sents=re.split(r'(?<=[.!?…\]])\s+(?!\[#)',p)
    for s in sents:
      sid=re.findall(r'\[#([a-z0-9]+)\]',s)
      if any(N[i]['trang_thai']=='so-bo' for i in sid if i in N) and not re.search('sơ bộ|chưa chính thức',s): err.append('Thiếu "sơ bộ": '+s[:80])
      if any(N[i]['trang_thai']=='tu-tinh' for i in sid if i in N) and not re.search('tính ra|tự tính',s,re.I): err.append('Thiếu "tính ra": '+s[:80])
    pass
  for p in [scr]:
    for s in re.split(r'(?<=[.!?…\]])\s+(?!\[#)',p):
      sid=re.findall(r'\[#([a-z0-9]+)\]',s)
      if any(N[i]['trang_thai']=='so-bo' for i in sid) and not re.search('sơ bộ|chưa chính thức',s): err.append('Màn hình thiếu sơ bộ: '+s[:80])
      if any(N[i]['trang_thai']=='tu-tinh' for i in sid) and not re.search('tự tính|tính ra',s): err.append('Màn hình thiếu nhãn tự tính: '+s[:80])
  for p in paras:
    nnum=len(set(re.findall(r'\[#([a-z0-9]+)',p)))
    if nnum>3: print('Cảnh báo đoạn dày số (>3 thẻ):',name,'|',p[:70])
  print(f'{name}: {w} từ')
print('TỔNG lời đọc:',total,'từ (âm tiết)')
first=' '.join(re.sub(r'\[#[a-z0-9]+\]','',beats[0].split('**Lời đọc:**')[1]).split()[:90])
print('90 từ đầu có [#]:', '[#' in ' '.join(beats[0].split('**Lời đọc:**')[1].split()[:95]))
last=' '.join(beats[-1].split('**Lời đọc:**')[1].split()[-60:]); print('60 từ cuối có ?:', '?' in last)
print('--- LỖI:',len(err)); [print(' ',e) for e in err]
