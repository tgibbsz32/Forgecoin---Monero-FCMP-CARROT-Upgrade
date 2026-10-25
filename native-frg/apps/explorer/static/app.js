'use strict';
const $ = id => document.getElementById(id);
const fmt = new Intl.NumberFormat();
const state = { generation: 0, searchSequence: 0, controller: null, refreshing: false, olderLoading: false, overview: true, next: null, fetched: null, blocks: [] };
function node(tag, text, cls) { const el = document.createElement(tag); if (text !== undefined) el.textContent = text; if (cls) el.className = cls; return el; }
function link(text, route, cls) { const el = node('a', text, cls); el.href = '#' + route; return el; }
function integer(value) { try { return BigInt(value).toLocaleString(); } catch { return '—'; } }
function coin(value) { try { const n = BigInt(value); const sign = n < 0n ? '-' : ''; const abs = n < 0n ? -n : n; return sign + (abs / 100000000n).toLocaleString() + '.' + (abs % 100000000n).toString().padStart(8, '0'); } catch { return '—'; } }
function date(value) { return value ? new Date(value * 1000).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' }) : 'Not available'; }
function duration(value) { if (value == null || !Number.isFinite(Number(value))) return '—'; return Number(value) < 60 ? `${Number(value).toFixed(1)} sec` : `${(Number(value) / 60).toFixed(1)} min`; }
function rate(value) { if (value == null || !Number.isFinite(Number(value))) return '—'; let n = Number(value), i = 0; const units = ['H/s', 'kH/s', 'MH/s', 'GH/s', 'TH/s']; while (n >= 1000 && i < units.length - 1) { n /= 1000; i++; } return `${n.toLocaleString(undefined, { maximumFractionDigits: 2 })} ${units[i]}`; }
function notice(message) { $('notice').textContent = message || ''; $('notice').hidden = !message; }
async function api(path, signal) { const response = await fetch(path, { signal, headers: { Accept: 'application/json' }, cache: 'no-store' }); let data; try { data = await response.json(); } catch { throw new Error('The explorer returned an unreadable response. Please try again.'); } if (!response.ok) { const err = new Error(data.error || 'The node is temporarily unavailable.'); err.status = response.status; throw err; } return data; }
function renderBlocks() {
  const body = $('blocks'); body.replaceChildren();
  if (!state.blocks.length) { const row = node('tr'); const cell = node('td', 'No blocks are available yet.', 'empty'); cell.colSpan = 6; row.append(cell); body.append(row); }
  for (const block of state.blocks) {
    const row = node('tr'); const height = node('td'); height.append(link(integer(block.height), `block/${block.height}`, 'height-link'));
    const hash = node('td'); const short = link(`${block.hash.slice(0, 12)}…${block.hash.slice(-8)}`, `block/${block.hash}`, 'hash'); short.title = block.hash; hash.append(short);
    row.append(height, hash, node('td', date(block.timestamp)), node('td', integer(block.tx_count), 'numeric'), node('td', coin(block.reward_atomic), 'numeric'), node('td', integer(block.difficulty), 'numeric')); body.append(row);
  }
  $('block-count').textContent = `${state.blocks.length} shown`;
  $('older').disabled = state.next == null || state.olderLoading;
  $('older').textContent = state.olderLoading ? 'Loading…' : state.next == null ? 'No older blocks' : 'Load older blocks ↓';
}
async function refreshOverview() {
  if (!state.overview || state.refreshing || state.olderLoading || document.hidden) return;
  const generation = state.generation;
  state.refreshing = true; $('refresh').disabled = true;
  try {
    const data = await api('/api/overview', state.controller.signal);
    if (generation !== state.generation) return;
    $('tip').replaceChildren(link(integer(data.tip_height), `block/${data.tip_height}`));
    $('difficulty').textContent = integer(data.difficulty);
    $('interval').textContent = duration(data.observed_interval_seconds);
    $('hashrate').textContent = rate(data.estimated_hashrate);
    $('target').textContent = `Recent average · target ${duration(data.target_seconds)}`;
    $('sync').textContent = data.synchronized ? 'Node synchronized' : 'Node is synchronizing';
    $('network-detail').textContent = `${fmt.format(data.peers)} peers · ${fmt.format(data.tx_pool_size)} pending transactions`;
    // Replace overlapping history after a reorganization, retaining only older pages.
    const oldest = data.blocks.length ? Math.min(...data.blocks.map(b => b.height)) : Infinity;
    state.blocks = [...data.blocks, ...state.blocks.filter(b => b.height < oldest)].sort((a, b) => b.height - a.height);
    state.next = state.blocks.length && state.blocks[state.blocks.length - 1].height > 0 ? state.blocks[state.blocks.length - 1].height - 1 : null;
    state.fetched = new Date(data.fetched_at * 1000); $('freshness').textContent = `Updated ${state.fetched.toLocaleTimeString()}`;
    renderBlocks(); notice('');
  } catch (error) {
    if (generation !== state.generation || error.name === 'AbortError') return;
    notice(`${state.fetched ? 'Displayed data may be stale. ' : ''}${error.message}`);
    $('freshness').textContent = state.fetched ? `Last success ${state.fetched.toLocaleTimeString()}` : 'Connection unavailable';
    if (!state.blocks.length) { $('blocks').replaceChildren(); const tr = node('tr'); const td = node('td', 'Unable to load blocks. Use Refresh to try again.', 'empty'); td.colSpan = 6; tr.append(td); $('blocks').append(tr); }
  } finally { if (generation === state.generation) { state.refreshing = false; $('refresh').disabled = false; } }
}
function row(list, label, value, cls) { const wrap = node('div', undefined, 'detail-row'); const dd = node('dd', undefined, cls); dd.append(value instanceof Node ? value : document.createTextNode(String(value))); wrap.append(node('dt', label), dd); list.append(wrap); }
function detailHeading(title, subtitle) { const target = $('detail-content'); target.replaceChildren(node('h2', title, 'detail-title'), node('p', subtitle, 'detail-subtitle')); const list = node('dl', undefined, 'detail-grid'); target.append(list); return list; }
function renderBlock(data) {
  const b = data.header; const list = detailHeading(`Block ${integer(b.height)}`, `${integer(data.confirmations)} confirmations${b.orphan_status ? ' · Orphan block' : ''}`);
  row(list, 'Block hash', b.hash, 'hash'); row(list, 'Mined', date(b.timestamp)); row(list, 'Difficulty', integer(b.difficulty)); row(list, 'Reward', `${coin(b.reward_atomic)} FORGE`); row(list, 'Size', `${integer(b.size)} bytes`); row(list, 'Protocol version', b.major_version);
  if (b.height > 0) row(list, 'Previous block', link(b.prev_hash, `block/${b.prev_hash}`, 'hash'));
  const section = node('section'); section.append(node('h2', 'Transactions')); const items = node('ul', undefined, 'tx-list');
  if (data.miner_tx_hash) { const item = node('li'); item.append(link(data.miner_tx_hash, `tx/${data.miner_tx_hash}`, 'hash'), node('span', 'Miner reward transaction', 'tx-label')); items.append(item); }
  for (const hash of data.tx_hashes) { const item = node('li'); item.append(link(hash, `tx/${hash}`, 'hash')); items.append(item); }
  if (!data.tx_hashes.length) items.append(node('li', 'No other transactions in this block.', 'muted'));
  section.append(items); $('detail-content').append(section);
}
function renderTx(data) {
  const list = detailHeading(data.coinbase ? 'Miner reward transaction' : 'Transaction', data.in_pool ? 'Pending · Waiting for a block' : `${integer(data.confirmations)} confirmations`);
  row(list, 'Transaction hash', data.hash, 'hash'); row(list, 'Status', data.in_pool ? 'Pending in the transaction pool' : 'Included in a block');
  if (data.block_height != null) row(list, 'Block', link(integer(data.block_height), `block/${data.block_height}`));
  row(list, 'Time', date(data.timestamp)); row(list, 'Fee', data.fee_atomic == null ? 'Not available' : `${coin(data.fee_atomic)} FORGE`);
  row(list, 'Version', data.version); row(list, 'Unlock time', integer(data.unlock_time)); row(list, 'Inputs', integer(data.inputs)); row(list, 'Outputs', integer(data.outputs)); row(list, data.coinbase ? 'Size' : 'Pruned data size', `${integer(data.size)} bytes`);
  $('detail-content').append(node('p', 'An unlock time is an on-chain value, not a guarantee that outputs are spendable. Miner rewards also have a maturity requirement.', 'muted'));
}
async function navigate() {
  state.controller?.abort(); state.controller = new AbortController(); const generation = ++state.generation; state.refreshing = false; state.olderLoading = false; $('refresh').disabled = false;
  notice(''); const route = location.hash.slice(1) || 'home'; state.overview = route === 'home';
  $('overview').hidden = !state.overview; $('detail').hidden = state.overview;
  if (state.overview) { document.title = 'ForgeCoin — Network explorer'; await refreshOverview(); return; }
  $('detail-content').replaceChildren(node('p', 'Loading ledger details…', 'muted'));
  const match = /^(block|tx)\/([a-fA-F0-9]+)$/.exec(route);
  if (!match || (match[1] === 'tx' && match[2].length !== 64) || (match[1] === 'block' && !/^\d+$/.test(match[2]) && match[2].length !== 64)) { $('detail-content').replaceChildren(node('h2', 'Invalid explorer link', 'detail-title'), node('p', 'Search for a block height or a full transaction hash.')); return; }
  try { const data = await api(`/api/${match[1]}/${encodeURIComponent(match[2])}`, state.controller.signal); if (generation !== state.generation) return; (match[1] === 'block' ? renderBlock : renderTx)(data); document.title = `${match[1] === 'block' ? 'Block ' + data.header.height : 'Transaction'} — ForgeCoin`; }
  catch (error) { if (generation !== state.generation || error.name === 'AbortError') return; $('detail-content').replaceChildren(node('h2', error.status === 404 ? 'Not found' : 'Unable to load details', 'detail-title'), node('p', error.message)); const retry = node('button', 'Try again', 'secondary'); retry.addEventListener('click', navigate); $('detail-content').append(retry); }
}
$('search').addEventListener('submit', async event => {
  event.preventDefault(); const query = $('query').value.trim(); const message = $('search-message'); const searchSequence = ++state.searchSequence;
  if (/^\d{1,9}$/.test(query)) { const route = `#block/${Number(query)}`; if (location.hash === route) navigate(); else location.hash = route; message.textContent = 'Enter a block number or a full 64-character hash.'; return; }
  if (!/^[a-fA-F0-9]{64}$/.test(query)) { message.textContent = 'Use a block number or a full 64-character hexadecimal hash.'; return; }
  const generation = state.generation; message.textContent = 'Looking up hash…'; const hash = query.toLowerCase();
  try { await api(`/api/block/${hash}`, state.controller.signal); if (generation === state.generation && searchSequence === state.searchSequence) { const route = `#block/${hash}`; if (location.hash === route) navigate(); else location.hash = route; } }
  catch (error) { if (generation !== state.generation || searchSequence !== state.searchSequence || error.name === 'AbortError') return; if (error.status === 404) { const route = `#tx/${hash}`; if (location.hash === route) navigate(); else location.hash = route; } else message.textContent = error.message; }
  finally { if (searchSequence === state.searchSequence && message.textContent === 'Looking up hash…') message.textContent = 'Enter a block number or a full 64-character hash.'; }
});
$('older').addEventListener('click', async () => {
  if (state.next == null || state.olderLoading || state.refreshing) return;
  state.olderLoading = true; const generation = state.generation; renderBlocks();
  try { const data = await api(`/api/blocks?before=${state.next}`, state.controller.signal); if (generation !== state.generation) return; const heights = new Set(state.blocks.map(b => b.height)); state.blocks.push(...data.blocks.filter(b => !heights.has(b.height))); state.next = data.next_before; notice(''); }
  catch (error) { if (generation === state.generation && error.name !== 'AbortError') notice(error.message); }
  finally { if (generation === state.generation) { state.olderLoading = false; renderBlocks(); } }
});
$('refresh').addEventListener('click', refreshOverview);
document.querySelector('.skip').addEventListener('click', event => { event.preventDefault(); $('content').focus(); });
window.addEventListener('hashchange', navigate);
document.addEventListener('visibilitychange', () => { if (!document.hidden) refreshOverview(); });
setInterval(refreshOverview, 10000);
navigate();
