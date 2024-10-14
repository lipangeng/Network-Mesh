import os
import hashlib
import subprocess
import threading
import time
from flask import Flask, jsonify, render_template

# 从环境变量获取WG命令
WG_COMMAND = os.getenv("WG_COMMAND", "wg show")

# PEERS
VAR_PEERS = {}

app = Flask(__name__)


def get_wireguard_runtime_info():
    """通过wg show命令获取Wireguard runtime info信息"""
    result = subprocess.run(WG_COMMAND, capture_output=True, text=True)
    peers_info = result.stdout
    return peers_info


def parse_peers_info(peers_info):
    """解析peer的endpoint信息"""
    peers = {}
    lines = peers_info.splitlines()
    peer_name = None

    for line in lines:
        if line.startswith('peer:'):
            peer_name = line.split()[1]
        elif line.startswith('endpoint:'):
            endpoint = line.split()[1]
            if peer_name:
                peers[peer_name] = {
                    'name': peer_name,
                    'endpoint': endpoint,
                    'endpoint_host': endpoint.split(':')[0],
                    'endpoint_port': endpoint.split(':')[1]
                }
                peer_name = None

    return peers


def sha256_hash(name):
    """对peer名称进行sha256哈希计算"""
    sha_signature = hashlib.sha256(name.encode()).hexdigest()
    return sha_signature


def update_peers_info_periodically(interval):
    while True:
        try:
            wg_info = get_wireguard_runtime_info()
            VAR_PEERS = parse_peers_info(wg_info)
        except Exception as e:
            print(f"Error updating peers info: {e}")
        time.sleep(interval)


@app.route('/peers', methods=['GET'])
def get_peers():
    try:
        return jsonify(VAR_PEERS)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/peer/<name>/endpoint', methods=['GET'])
def get_peer_endpoint(name):
    try:
        return jsonify(VAR_PEERS[name])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/peer/<name>/sing-box', methods=['GET'])
def get_peer_sing_box(name):
    try:
        peer_info = VAR_PEERS[name]
        if peer_info['endpoint']:
            with open('templates/' + name + '.json', 'r') as file:
                json_template = file.read()
                return jsonify(json_template.format(**VAR_PEERS))
        return jsonify({})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    # 启动一个新线程来定期更新peers信息
    update_thread = threading.Thread(target=update_peers_info_periodically, args=(10,))  # 每10秒更新一次
    update_thread.daemon = True  # 设置为守护线程，这样当主线程结束时，它也会自动结束
    update_thread.start()

    app.run(host='0.0.0.0', port=8080)


if __name__ == "__main__":
    main()
