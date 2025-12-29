"""
kubu_network_bootstrap.py
-------------------------
Fully networked Kubu multi-language dev ecosystem:
- Python, Node, Go, Rust, Java, Ruby, JS
- AI container with GPU support
- Blockchain node
- Auto Docker network for seamless container communication
"""

import sys
import os
import subprocess
import docker
import requests
from .version import __version__

# =========================
# Platform Detection
# =========================
IS_WINDOWS_PLATFORM = (sys.platform == 'win32')

# =========================
# Docker Endpoint
# =========================
DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_UNIX_SOCKET = "http+unix:///var/run/docker.sock"
DEFAULT_NPIPE = 'npipe:////./pipe/docker_engine'

def get_default_docker_endpoint():
    if IS_WINDOWS_PLATFORM:
        if os.path.exists(r'\\.\pipe\docker_engine'):
            return DEFAULT_NPIPE
        return f"tcp://{DEFAULT_HTTP_HOST}:2375"
    else:
        if os.path.exists("/var/run/docker.sock"):
            return DEFAULT_UNIX_SOCKET
        return f"tcp://{DEFAULT_HTTP_HOST}:2375"

DOCKER_ENDPOINT = get_default_docker_endpoint()

# =========================
# Docker Client
# =========================
client = docker.DockerClient(base_url=DOCKER_ENDPOINT, version='1.45')

# =========================
# GPU Detection
# =========================
def detect_nvidia_gpus():
    try:
        subprocess.check_output(["nvidia-smi"], stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False

HAS_GPU = detect_nvidia_gpus()

# =========================
# Blockchain Node
# =========================
DEFAULT_BLOCKCHAIN_NODE = "http://127.0.0.1:8545"

def check_blockchain_node(node_url=DEFAULT_BLOCKCHAIN_NODE):
    try:
        resp = requests.get(node_url)
        if resp.status_code == 200:
            print(f"[INFO] Blockchain node {node_url} reachable.")
            return True
        else:
            print(f"[WARNING] Blockchain node {node_url} returned status {resp.status_code}.")
            return False
    except Exception as e:
        print(f"[ERROR] Cannot reach blockchain node {node_url}: {e}")
        return False

# =========================
# Helpers
# =========================
BYTE_UNITS = {'b':1, 'k':1024, 'm':1024*1024, 'g':1024*1024*1024}
def bytes_from_human(size_str: str) -> int:
    unit = size_str[-1].lower()
    number = int(size_str[:-1])
    return number * BYTE_UNITS.get(unit, 1)

def ensure_image(image_name):
    try:
        client.images.get(image_name)
        print(f"[INFO] Image {image_name} exists locally.")
    except docker.errors.ImageNotFound:
        print(f"[INFO] Pulling {image_name}...")
        client.images.pull(image_name)
        print(f"[INFO] Pulled {image_name} successfully.")

# =========================
# Network Creation
# =========================
DEFAULT_NETWORK_NAME = "kubu_network"

def create_network(network_name=DEFAULT_NETWORK_NAME):
    try:
        net = client.networks.get(network_name)
        print(f"[INFO] Network '{network_name}' already exists.")
        return net
    except docker.errors.NotFound:
        net = client.networks.create(network_name, driver="bridge")
        print(f"[INFO] Network '{network_name}' created.")
        return net

# =========================
# Multi-Language Dev Containers
# =========================
DEFAULT_MULTI_LANGUAGE_IMAGES = {
    "python": "python:3.12-slim",
    "node": "node:20-slim",
    "go": "golang:1.21-alpine",
    "rust": "rust:1.76-slim",
    "java": "openjdk:21-slim",
    "ruby": "ruby:3.4-slim",
    "js": "node:20-slim"
}

DEFAULT_MULTI_LANGUAGE_RESOURCES = {
    "python": {"memory": "2g", "cpus": 1},
    "node": {"memory": "2g", "cpus": 1},
    "go": {"memory": "1g", "cpus": 1},
    "rust": {"memory": "2g", "cpus": 1},
    "java": {"memory": "3g", "cpus": 2},
    "ruby": {"memory": "1g", "cpus": 1},
    "js": {"memory": "2g", "cpus": 1}
}

def create_dev_container(lang, network, image=None, resources=None):
    """
    Create or start a container for a specific dev language connected to the Kubu network.
    """
    image_name = image or DEFAULT_MULTI_LANGUAGE_IMAGES.get(lang)
    resources = resources or DEFAULT_MULTI_LANGUAGE_RESOURCES.get(lang, {"memory": "1g", "cpus": 1})
    
    ensure_image(image_name)
    container_name = f"kubu_{lang}_container"
    
    try:
        container = client.containers.get(container_name)
        print(f"[INFO] Container '{container_name}' already exists.")
        if network:
            network.connect(container)
        return container
    except docker.errors.NotFound:
        container = client.containers.run(
            image=image_name,
            name=container_name,
            detach=True,
            mem_limit=resources.get("memory"),
            cpus=resources.get("cpus"),
            network=network.name if network else None
        )
        print(f"[INFO] Container '{container_name}' created and connected to network '{network.name}'.")
        return container

# =========================
# AI Container
# =========================
DEFAULT_AI_CONTAINER_IMAGE = "kubu/ai-base:latest"
DEFAULT_AI_CONTAINER_RESOURCES = {"memory": "4g", "cpus": 2}

def create_ai_container(network, name="kubu_ai_container"):
    ensure_image(DEFAULT_AI_CONTAINER_IMAGE)
    
    runtime_params = {}
    if HAS_GPU:
        runtime_params['device_requests'] = [
            docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])
        ]
        print("[INFO] AI container will use GPU.")
    else:
        print("[INFO] AI container will use CPU only.")

    container = client.containers.run(
        image=DEFAULT_AI_CONTAINER_IMAGE,
        name=name,
        detach=True,
        mem_limit=DEFAULT_AI_CONTAINER_RESOURCES["memory"],
        cpus=DEFAULT_AI_CONTAINER_RESOURCES["cpus"],
        network=network.name,
        **runtime_params
    )
    print(f"[INFO] AI container '{name}' started on network '{network.name}'.")
    return container

# =========================
# Full Kubu Networked Bootstrap
# =========================
def kubu_network_bootstrap(languages=None, start_ai=True):
    """
    Full Kubu multi-language networked bootstrap:
    - languages: list of languages to start
    - start_ai: whether to start AI container
    """
    print("=== KUBU NETWORK BOOTSTRAP START ===")
    
    # 1. Check blockchain node
    check_blockchain_node()
    
    # 2. Create Kubu network
    network = create_network()
    
    # 3. Start dev containers
    languages = languages or list(DEFAULT_MULTI_LANGUAGE_IMAGES.keys())
    dev_containers = {}
    for lang in languages:
        dev_containers[lang] = create_dev_container(lang, network)
    
    # 4. Start AI container if requested
    ai_container = None
    if start_ai:
        ai_container = create_ai_container(network)
    
    print("=== KUBU NETWORK BOOTSTRAP COMPLETE ===")
    return {"network": network, "dev_containers": dev_containers, "ai_container": ai_container}
