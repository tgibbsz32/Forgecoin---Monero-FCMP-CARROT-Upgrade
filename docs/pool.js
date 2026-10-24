'use strict';
// Static placeholder only: no pool API, wallet credentials or fabricated metrics.
document.querySelector('#worker-lookup')?.addEventListener('submit',e=>{
  e.preventDefault();
  const out=document.querySelector('#worker-result');
  if(out)out.textContent='Worker lookup is not available: the native FRG mining pool and its verified API are not deployed. Do not submit private wallet data.';
});