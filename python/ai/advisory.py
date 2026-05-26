import sys
import subprocess
import json
import sqlite3
import pathlib
import os

# Add parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from ai.providers.factory import ProviderFactory

class AdvisoryEngine:
    def __init__(self):
        self.provider = ProviderFactory.get_provider()

    def _run_cmd(self, cmd):
        try:
            return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
        except Exception:
            return ""

    def analyze_docker_resources(self):
        print("Gathering Docker state...")
        images = self._run_cmd(["docker", "images", "--format", "{{.Repository}}:{{.Tag}} ({{.Size}})"])
        containers = self._run_cmd(["docker", "ps", "-a", "--format", "{{.Names}} - {{.Status}}"])
        volumes = self._run_cmd(["docker", "volume", "ls", "--format", "{{.Name}}"])
        
        telemetry = f"Docker State:\nImages:\n{images}\nContainers:\n{containers}\nVolumes:\n{volumes}"
        print("Consulting AI provider...")
        return self.provider.generate_recommendation(telemetry)

    def analyze_apt_packages(self):
        print("Gathering APT package state...")
        manual_pkgs = self._run_cmd(["apt-mark", "showmanual"])
        autoremove = self._run_cmd(["apt-get", "-s", "autoremove"])
        
        telemetry = f"Apt State:\nManually installed packages summary (first 20 lines):\n{chr(10).join(manual_pkgs.splitlines()[:20])}\nAutoremove simulation:\n{autoremove}"
        print("Consulting AI provider...")
        return self.provider.generate_recommendation(telemetry)

    def estimate_reclaimable_storage(self):
        print("Analyzing SysClean queue...")
        DB_PATH = pathlib.Path.home() / ".local/share/sysclean/sysclean.db"
        if not DB_PATH.exists():
            return {"error": "No active queue database found."}
            
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        cursor = conn.cursor()
        cursor.execute("SELECT module, payload_json FROM queue WHERE status IN ('PROPOSED', 'APPROVED')")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {"error": "No pending cleanup tasks found."}
            
        summary = []
        total_bytes = 0
        for mod, payload_str in rows:
            if payload_str:
                try:
                    data = json.loads(payload_str)
                    bytes_est = data.get("estimated_bytes", 0)
                    total_bytes += bytes_est
                    summary.append(f"- Module '{mod}' claims it can reclaim {bytes_est / (1024*1024):.1f} MB")
                except json.JSONDecodeError:
                    pass
                    
        total_mb = total_bytes / (1024*1024)
        telemetry = f"Queue Tasks:\n" + "\n".join(summary) + f"\nTotal estimated savings: {total_mb:.1f} MB."
        print("Consulting AI provider...")
        return self.provider.generate_recommendation(telemetry)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 advisory.py [docker|apt|storage]")
        sys.exit(1)
        
    engine = AdvisoryEngine()
    target = sys.argv[1]
    
    if target == "docker":
        res = engine.analyze_docker_resources()
    elif target == "apt":
        res = engine.analyze_apt_packages()
    elif target == "storage":
        res = engine.estimate_reclaimable_storage()
    else:
        print(f"Unknown target: {target}")
        sys.exit(1)
        
    print("\n--- AI Recommendation ---")
    if isinstance(res, dict) and "response" in res:
        print(res["response"])
    elif isinstance(res, dict) and "error" in res:
        print(f"Error: {res['error']}")
        if "ConnectionError" in res["error"]:
            print("\nHint: If you're trying to use Ollama, make sure the service is running.")
            print("Alternatively, to use Google Gemini, create a '.env' file in the project root with:")
            print("SYSCLEAN_AI_PROVIDER=google")
            print("GOOGLE_API_KEY=your_api_key_here")
    else:
        print(res)
