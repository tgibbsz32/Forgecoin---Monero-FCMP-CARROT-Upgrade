import json,random
from pathlib import Path
from difficulty_model import old, lwma
root=Path(__file__).resolve().parent
cases=[]
def add(h,m,hist,expected=None):
 if expected is None:
  d=lwma(hist,90) if m and h>=700 else old(hist)
  expected=max(d,1000000 if h>=600 else 500000) if m and h>=500 and d else d
 cases.append((h,m,list(hist),expected))
hist=[];cum=0
for b in json.loads((root/'historical-headers.json').read_text()):
 add(b['height'],1,hist,b['difficulty']);cum+=b['difficulty'];hist.append((b['timestamp'],cum))
rng=random.Random(744)
for k in range(80):
 hist=[];t=100000;cum=0
 for i in range(735):
  t=max(10000,t+rng.randint(-300,1500));cum+=rng.randint(1,10000000);hist.append((t,cum))
 for height in [499,500,599,600,699,700,701]: add(height,1,hist)
 add(700,0,hist)
 # Rolling cache, fresh history and alternative-chain merged history must agree.
 add(700,1,hist[-91:]);add(701,1,hist[:650]+hist[650:])
hist=[(i*120,(i+1)*12000000) for i in range(735)]
add(700,1,hist,11880000)
add(700,1,[(i, i+1) for i in range(91)],1000000)
add(700,1,hist[:90],0)
add(700,1,[(0,1)]*91,0)
add(700,1,[(2**64-1,i+1) for i in range(91)],0)
# Exact huge arithmetic plus overflow rejection.
add(700,1,[(i*120,(i+1)*(2**110)) for i in range(91)])
add(700,1,[(i,(i+1)*(2**120)) for i in range(91)])
with (root/'lwma-vectors.txt').open('w') as f:
 for h,m,hist,expected in cases:
  f.write(f'{h} {m} {len(hist)} {expected}\n')
  for t,c in hist:f.write(f'{t} {c}\n')
print(len(cases),'vectors written')


