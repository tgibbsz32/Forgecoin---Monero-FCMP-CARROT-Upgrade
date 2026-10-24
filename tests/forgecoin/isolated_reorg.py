#!/usr/bin/env python3
"""Native candidate reorg test using copied LMDBs and offline loopback RPC only.

Requires a stopped source checkpoint. Never opens that database with a daemon.
Runs real PoW (no difficulty override); output directory must not already exist.
"""
import argparse
import hashlib
import json
import pathlib
import shutil
import socket
import subprocess
import time
import urllib.request


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def manifest(root):
    return {str(p.relative_to(root)): digest(p) for p in sorted(root.rglob('*')) if p.is_file()}


class Node:
    def __init__(self, name, args, port):
        self.name, self.args, self.port = name, args, port
        self.root = args.output / name
        self.proc = None
        self.streams = []
        self.generation = 0

    def request(self, endpoint, body=None):
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(f'http://127.0.0.1:{self.port}/{endpoint}', data,
                                     {'Content-Type': 'application/json'})
        with urllib.request.urlopen(req, timeout=30) as response:
            result = json.load(response)
        require('error' not in result, str(result))
        result = result.get('result', result)
        require(result.get('status', 'OK') == 'OK', str(result))
        return result

    def rpc(self, method, params=None):
        return self.request('json_rpc', {'jsonrpc': '2.0', 'id': 'reorg',
                                        'method': method, 'params': {} if params is None else params})

    def info(self):
        info = self.request('get_info')
        require(info['incoming_connections_count'] == 0 and info['outgoing_connections_count'] == 0,
                'Offline node unexpectedly has peers')
        return info

    def start(self):
        self.generation += 1
        command = [str(self.args.daemon), '--offline', '--data-dir', str(self.root),
                   '--log-file', str(self.root / 'daemon.log'), '--rpc-bind-ip', '127.0.0.1',
                   '--rpc-bind-port', str(self.port), '--p2p-bind-ip', '127.0.0.1',
                   '--p2p-bind-port', str(self.port - 1), '--no-zmq', '--no-igd',
                   '--disable-dns-checkpoints', '--non-interactive']
        for port in (self.port, self.port - 1):
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', port))
        self.streams = [(self.root / f'{kind}-{self.generation}.txt').open('w')
                        for kind in ('stdout', 'stderr')]
        self.proc = subprocess.Popen(command, stdout=self.streams[0], stderr=self.streams[1],
                                     creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0)
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            require(self.proc.poll() is None, f'{self.name} daemon exited during startup')
            try:
                return self.info()
            except (OSError, ValueError):
                time.sleep(1)
        raise TimeoutError('RPC startup timeout')

    def stop(self):
        if self.proc and self.proc.poll() is None:
            try:
                try:
                    self.request('stop_mining', {})
                except RuntimeError as error:
                    if 'Mining never started' not in str(error):
                        raise
                self.request('stop_daemon', {})
                self.proc.wait(timeout=45)
            except Exception:
                self.proc.terminate()
                self.proc.wait(timeout=15)
                raise
        for stream in self.streams:
            stream.close()

    def mine(self, target):
        self.request('start_mining', {'miner_address': self.args.address, 'threads_count': self.args.threads,
                                     'do_background_mining': False, 'ignore_battery': True})
        deadline = time.monotonic() + self.args.timeout
        last = None
        try:
            while time.monotonic() < deadline:
                info = self.info()
                if info['height'] != last:
                    print(f'{self.name}: height={info["height"]} work={info["wide_cumulative_difficulty"]} tip={info["top_block_hash"]}', flush=True)
                    last = info['height']
                if info['height'] >= target:
                    return info
                time.sleep(0.5)
            raise TimeoutError(f'{self.name} did not reach {target} within {self.args.timeout}s')
        finally:
            self.request('stop_mining', {})


def work(info):
    return int(info['wide_cumulative_difficulty'], 16)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--daemon', required=True, type=pathlib.Path)
    parser.add_argument('--checkpoint', required=True, type=pathlib.Path)
    parser.add_argument('--expected-tip', required=True)
    parser.add_argument('--expected-height', type=int, default=17, help='RPC chain length, including genesis')
    parser.add_argument('--address', required=True)
    parser.add_argument('--output', required=True, type=pathlib.Path)
    parser.add_argument('--rpc-port', type=int, default=40581)
    parser.add_argument('--threads', type=int, default=6)
    parser.add_argument('--timeout', type=int, default=1800, help='Seconds per mining branch')
    args = parser.parse_args()
    args.daemon, args.checkpoint, args.output = (p.resolve() for p in (args.daemon, args.checkpoint, args.output))
    require(args.output != args.checkpoint and args.checkpoint not in args.output.parents,
            'Output must be outside the checkpoint')
    require(not args.output.exists(), 'Output already exists; use a new directory')
    original = manifest(args.checkpoint)
    require('lmdb\\data.mdb' in original or 'lmdb/data.mdb' in original, 'Missing LMDB checkpoint')
    args.output.mkdir(parents=True)
    evidence = {'daemon_sha256': digest(args.daemon), 'checkpoint_before': original,
                'transport': 'offline RPC submit_block; no peer connections', 'steps': [], 'passed': False}

    def save():
        (args.output / 'evidence.json').write_text(json.dumps(evidence, indent=2) + '\n')

    def handoff(number, title, details):
        evidence['steps'].append({'step': number, 'title': title, 'details': details})
        (args.output / f'STEP{number}_HANDOFF.md').write_text(f'# Step {number}: {title}\n\n{details}\n', encoding='utf-8')
        save()
        print(f'HANDOFF {number}: {title}', flush=True)

    nodes = [Node('A', args, args.rpc_port), Node('B', args, args.rpc_port + 100)]
    try:
        for node in nodes:
            (node.root / 'lmdb').mkdir(parents=True)
            shutil.copy2(args.checkpoint / 'lmdb' / 'data.mdb', node.root / 'lmdb' / 'data.mdb')
            require(digest(node.root / 'lmdb' / 'data.mdb') == digest(args.checkpoint / 'lmdb' / 'data.mdb'), 'Copy mismatch')
        a, b = nodes
        starts = [node.start() for node in nodes]
        for info in starts:
            require(info['height'] == args.expected_height and info['top_block_hash'] == args.expected_tip,
                    'Checkpoint does not match expected height/tip')
        evidence['starts'] = starts
        handoff(2, 'Copied checkpoint verified', f'Both offline nodes match RPC height {args.expected_height}, tip {args.expected_tip}. Source database was copied, never opened by the test daemon. Next: mine divergent native-PoW branches.')
        a.mine(args.expected_height + 2)
        ai = a.info()
        b.mine(ai['height'] + 1)
        bi = b.info()
        require(work(bi) > work(ai), 'B must have more cumulative work')
        a_blocks = [a.rpc('get_block', {'height': h}) for h in range(args.expected_height, ai['height'])]
        b_blocks = [b.rpc('get_block', {'height': h}) for h in range(args.expected_height, bi['height'])]
        require(a_blocks[0]['block_header']['hash'] != b_blocks[0]['block_header']['hash'], 'Branches did not diverge')
        require(a_blocks[0]['block_header']['prev_hash'] == b_blocks[0]['block_header']['prev_hash'] == args.expected_tip, 'Wrong fork parent')
        evidence.update(branch_a=ai, branch_b=bi, a_blocks=a_blocks, b_blocks=b_blocks)
        handoff(3, 'Competing branches mined', f'A: height {ai["height"]}, work {work(ai)}, tip {ai["top_block_hash"]}. B: height {bi["height"]}, work {work(bi)}, tip {bi["top_block_hash"]}. First post-checkpoint blocks differ and share the verified parent. Next: deliver B blocks to A in order and assert fork choice.')
        transitions = []
        for block in b_blocks:
            a.rpc('submit_block', [block['blob']])
            current = a.info()
            header = block['block_header']
            candidate_work = int(header['wide_cumulative_difficulty'], 16)
            if candidate_work <= work(ai):
                require(current['top_block_hash'] == ai['top_block_hash'], 'Non-heavier branch replaced incumbent')
            else:
                require(current['top_block_hash'] == header['hash'], 'Heavier branch was not adopted')
            transitions.append({'submitted': header, 'observed': current})
        require(a.info()['top_block_hash'] == bi['top_block_hash'], 'Final tips differ')
        for block in a_blocks:
            header = a.rpc('get_block_header_by_hash', {'hash': block['block_header']['hash']})['block_header']
            require(header['orphan_status'], 'Displaced A block is not marked orphan')
        for block in b_blocks:
            header = a.rpc('get_block_header_by_height', {'height': block['block_header']['height']})['block_header']
            require(header['hash'] == block['block_header']['hash'], 'Winning canonical block mismatch')
        evidence.update(transitions=transitions, alternate_chains=a.rpc('get_alternate_chains'))
        handoff(4, 'Heavier competing chain adopted', 'A retained its tip while B had no more cumulative work, then reorganized to B when B exceeded it. Canonical B block hashes and orphan status of displaced A blocks verified. Next: restart both nodes and verify persistence and source preservation. Wallet recovery and P2P transport are not covered.')
        for node in nodes:
            node.stop()
        restarted = [node.start() for node in nodes]
        for info in restarted:
            require(info['top_block_hash'] == bi['top_block_hash'] and work(info) == work(bi), 'Restart lost winning chain')
        evidence['restarted'] = restarted
        evidence['passed'] = True
    except BaseException as error:
        evidence['error'] = str(error)
        raise
    finally:
        errors = []
        for node in nodes:
            try:
                node.stop()
            except Exception as error:
                errors.append(str(error))
        evidence['checkpoint_after'] = manifest(args.checkpoint)
        evidence['source_preserved'] = evidence['checkpoint_after'] == original
        evidence['cleanup_errors'] = errors
        evidence['passed'] = evidence['passed'] and evidence['source_preserved'] and not errors
        save()
        handoff(5, 'Final verification' if evidence['passed'] else 'Incomplete test',
                f'Passed: {evidence["passed"]}. Source checkpoint byte-for-byte unchanged: {evidence["source_preserved"]}. Cleanup errors: {errors}. Details: evidence.json. No Oracle or live-chain access. No wallet, ARM64, height 90Ã¢â‚¬â€œ92 or release approval claim.')
        require(evidence['passed'], 'Test incomplete; inspect evidence.json')


if __name__ == '__main__':
    main()
