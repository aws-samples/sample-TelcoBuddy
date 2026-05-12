"""Kubectl helper for Lambda."""
import os, subprocess
KUBECTL_PATH = os.path.join(os.path.dirname(__file__), "kubectl")
def run(args, env=None):
    result = subprocess.run([KUBECTL_PATH] + args, capture_output=True, text=True, env=env)
    return result.stdout, result.stderr, result.returncode
