'use strict';
/* Offline illustrative PoW math. No live service or payout promises. */
const ids=['user-hash','network-hash','pool-hash','network-diff','share-diff','reward','fee','block-target'];
const $=id=>document.getElementById(id);
const nf=(n,d=2)=>Number.isFinite(n)?n.toLocaleString('en-US',{maximumFractionDigits:d}):'Unavailable';
const time=s=>{if(!Number.isFinite(s))return 'Unavailable';if(s<60)return nf(s)+' sec';if(s<3600)return nf(s/60)+' min';if(s<86400)return nf(s/3600)+' hours';return nf(s/86400)+' days';};
function render(){
 const [u,n,p,d,sd,reward,fee,target]=ids.map(id=>Number($(id).value));
 const valid=[u,n,p,d,sd,reward,fee,target].every(Number.isFinite)&&u>0&&n>0&&p>0&&d>0&&sd>0&&reward>=0&&target>0&&fee>=0&&fee<=100&&u<=p&&p<=n;
 const error=$('calc-error');
 error.textContent=valid?'Estimates use the entered values; none are live network measurements.':'Enter positive finite hashrates/difficulties and block target. Require user hashrate <= pool hashrate <= network hashrate; fee must be between 0 and 100%.';
 const keys=['daily-solo','daily-pool','share-mean','daily-shares','solo-mean','solo-blocks','pool-mean','pool-blocks','network-mean','pool-percent','pool-diff-output','network-diff-output'];
 if(!valid){keys.forEach(k=>$(k).textContent='Unavailable');$('effort-body').replaceChildren();$('effort-chart').replaceChildren();return;}
 const blocksU=u*86400/d,blocksP=p*86400/d;
 const values={
 'daily-solo':nf(blocksU*reward,6)+' FRG',
 'daily-pool':nf(blocksP*reward*(u/p)*(1-fee/100),6)+' FRG',
 'share-mean':time(sd/u),
 'daily-shares':nf(u*86400/sd,3),
 'solo-mean':time(d/u),
 'solo-blocks':nf(blocksU,5),
 'pool-mean':time(d/p),
 'pool-blocks':nf(blocksP,5),
 'network-mean':time(d/n),
 'pool-percent':nf(100*p/n)+'%',
 'pool-diff-output':nf(sd,0)+' (share target)',
 'network-diff-output':nf(d,0)
 };
 for(const [k,v] of Object.entries(values))$(k).textContent=v;
 const body=$('effort-body');body.replaceChildren();
 [25,50,75,100,125,150,200,300,500,750,1000].forEach(percent=>{
  const chance=100*(-Math.expm1(-percent/100));
  const tr=document.createElement('tr');
  [percent+'%',nf(chance,3)+'%',nf(chance,3)+'%',time((sd/u)*(percent/100))].forEach(value=>{const td=document.createElement('td');td.textContent=value;tr.append(td);});body.append(tr);
 });
 const svg=$('effort-chart');svg.replaceChildren();const ns='http://www.w3.org/2000/svg';
 const line=(tag,attrs,content)=>{const e=document.createElementNS(ns,tag);for(const [k,v] of Object.entries(attrs))e.setAttribute(k,v);if(content!==undefined)e.textContent=content;svg.append(e);return e;};
 for(let q=0;q<=4;q++){const y=240-200*q/4;line('line',{x1:65,y1:y,x2:690,y2:y,stroke:'#26425c','stroke-width':1});line('text',{x:12,y:y+5,fill:'#b4cde1','font-size':13},q*25+'%');}
 for(let q=0;q<=5;q++){const x=65+625*q/5;line('line',{x1:x,y1:40,x2:x,y2:240,stroke:'#19364e'});line('text',{x:x-12,y:263,fill:'#b4cde1','font-size':12},q*200+'%');}
 const pts=[];for(let i=0;i<=200;i++){const e=i/20;pts.push((65+i*625/200).toFixed(1)+','+(240-200*(-Math.expm1(-e))).toFixed(1));}
 line('polyline',{points:pts.join(' '),fill:'none',stroke:'#46c5f8','stroke-width':3});
 line('text',{x:300,y:18,fill:'#e8f6ff','font-size':15},'Probability of ≥1 discovery');
}
ids.forEach(id=>$(id)?.addEventListener('input',render));render();
