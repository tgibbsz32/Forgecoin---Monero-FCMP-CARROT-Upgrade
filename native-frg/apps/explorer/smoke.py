import json
from app import app
c=app.test_client()
o=c.get('/api/overview');assert o.status_code==200,o.data
j=o.json;print('overview',j['height'],j['tip_hash'])
b=c.get('/api/block/'+str(j['tip_height']));assert b.status_code==200,b.data;print('block',b.json)
t=c.get('/api/tx/'+b.json['miner_tx_hash']);assert t.status_code==200,t.data;print('coinbase',t.json)
for url,code in [('/api/block/-1',400),('/api/block/99999999',404),('/api/tx/not-a-hash',400),('/api/blocks?before=0',200),('/api/blocks?before=1.2',400),('/api/stop_daemon',404)]:
 r=c.get(url);assert r.status_code==code,(url,r.status_code)
assert c.post('/api/overview').status_code==405
print('Read-only, pagination, lookup and input validation smoke tests passed')
