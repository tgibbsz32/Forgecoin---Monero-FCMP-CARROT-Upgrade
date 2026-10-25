import json, random, statistics
from pathlib import Path

def old(hist):
 w=hist[-735:][:720]; t=sorted(x[0] for x in w); n=len(t)
 if n<2:return 1
 a=0 if n<=600 else (n-600+1)//2;b=n if n<=600 else a+600
 return ((w[b-1][1]-w[a][1])*120+max(1,t[b-1]-t[a])-1)//max(1,t[b-1]-t[a])
def lwma(hist,n):
 w=hist[-(n+1):];prev=w[0][0];L=0
 for i in range(1,n+1):
  now=max(w[i][0],prev+1);L+=i*min(720,now-prev);prev=now
 L=max(L,n*n*120//20)
 return (w[-1][1]-w[0][1])*120*(n+1)*99//(200*L)
def run(name,n,kind,seed=None):
 rng=random.Random(seed);h=[(i*120,(i+1)*12000000) for i in range(735)];clock=float(h[-1][0]);cum=h[-1][1]
 ds=[];dt=[]
 for i in range(1600):
  rate=100000
  if i>=800:
   if kind=='up':rate*=10
   if kind=='down':rate/=10
   if kind=='switch' and (i-800)//30%2==0:rate*=10
   if kind=='pause' and i==800:clock+=86400
  d=max(1000000,old(h) if n==0 else lwma(h,n));elapsed=d/rate*(rng.expovariate(1) if seed is not None else 1)
  clock+=elapsed;cum+=d;h.append((int(clock),cum));h=h[-735:]
  if i>=800:dt.append(elapsed);ds.append(d)
 return {'first100':statistics.mean(dt[:100]),'last100':statistics.mean(dt[-100:]),'maxInterval':max(dt),'difficultyCV':statistics.pstdev(ds)/statistics.mean(ds)}
