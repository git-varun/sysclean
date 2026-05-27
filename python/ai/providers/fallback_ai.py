"""Fallback Heuristic AI Provider when Ollama/Gemini are offline."""
import re
from ai.providers.base import AIProvider

class FallbackAIProvider(AIProvider):
    """Generates high-quality structured heuristic recommendations when LLMs are offline."""

    def generate_recommendation(self, telemetry):
        # Determine the target from the telemetry contents
        if "Docker State:" in telemetry:
            return self._analyze_docker(telemetry)
        elif "Apt State:" in telemetry:
            return self._analyze_apt(telemetry)
        elif "Queue Tasks:" in telemetry:
            return self._analyze_storage(telemetry)
        else:
            return self._generic_advice(telemetry)

    def _get_header(self, title):
        return (
            f"### 🤖 SysClean AI Advisory: {title}\n"
            f"> [!NOTE]\n"
            f"> The system is operating in **Local Heuristic Mode** because no external AI provider "
            f"could be reached. To enable full LLM analysis, see the configuration guide below.\n\n"
        )

    def _get_footer(self):
        return (
            "\n---\n"
            "#### ⚙️ How to Enable Advanced LLM Advisory\n"
            "To unlock full neural network recommendations, choose one of the options below:\n\n"
            "1. **Option A: Google Gemini (Recommended)**\n"
            "   - Create/edit the `.env` file in the project root:\n"
            "     ```ini\n"
            "     SYSCLEAN_AI_PROVIDER=google\n"
            "     GOOGLE_API_KEY=your_actual_gemini_api_key\n"
            "     ```\n"
            "2. **Option B: Local Ollama**\n"
            "   - Install Ollama (`curl -fsSL https://ollama.com/install.sh | sh`)\n"
            "   - Start the service and pull the default model: `ollama pull llama3`\n"
        )

    def _analyze_docker(self, telemetry):
        # Extract images, containers, volumes
        images = []
        containers = []
        volumes = []
        
        current_section = None
        for line in telemetry.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith("Images:"):
                current_section = "images"
                continue
            elif line.startswith("Containers:"):
                current_section = "containers"
                continue
            elif line.startswith("Volumes:"):
                current_section = "volumes"
                continue
            
            if current_section == "images" and not line.startswith("Docker State:"):
                images.append(line)
            elif current_section == "containers":
                containers.append(line)
            elif current_section == "volumes":
                volumes.append(line)

        report = self._get_header("Docker Optimization Analysis")
        
        report += "#### 🔍 Observations\n"
        report += f"- Found **{len(images)}** Docker image tags stored locally.\n"
        report += f"- Found **{len(containers)}** defined containers (active or stopped).\n"
        report += f"- Found **{len(volumes)}** local persistent storage volumes.\n\n"

        report += "#### 💡 Recommendations\n"
        if len(containers) > 0:
            stopped = [c for c in containers if "Exited" in c or "Created" in c]
            report += f"- **Prune Stopped Containers:** There are {len(stopped)} stopped containers. Run `docker container prune` to clean up resources.\n"
        if len(images) > 0:
            dangling = [img for img in images if "<none>" in img]
            if dangling:
                report += f"- **Clean Dangling Images:** Found {len(dangling)} dangling build layers. Run `docker image prune` to reclaim space.\n"
            else:
                report += "- **Review Large Images:** Check if older application base images are still required for your daily development workflow.\n"
        if len(volumes) > 0:
            report += "- **Volume Inspection:** Orphan volumes can accumulate. Run `docker volume prune` to clear unreferenced volumes (ensure database volumes are backed up first!).\n"

        report += "\n#### ⚠️ Safety Warning\n"
        report += "> [!IMPORTANT]\n"
        report += "> Before running any destructive docker prune command, verify that active local databases or code volumes are registered in docker-compose configs to prevent data loss.\n"

        report += self._get_footer()
        return {"response": report}

    def _analyze_apt(self, telemetry):
        manual_count = 0
        autoremove_lines = []
        
        in_autoremove = False
        for line in telemetry.splitlines():
            if "Manually installed packages summary" in line:
                continue
            if "Autoremove simulation:" in line:
                in_autoremove = True
                continue
            
            if not in_autoremove:
                if line.strip() and not line.startswith("Apt State:"):
                    manual_count += 1
            else:
                if line.strip():
                    autoremove_lines.append(line)

        report = self._get_header("APT Package Management Analysis")
        
        report += "#### 🔍 Observations\n"
        report += f"- Identified manually-installed packages (showing sample subset).\n"
        
        auto_count = 0
        for line in autoremove_lines:
            if line.startswith("Remv "):
                auto_count += 1

        if auto_count > 0:
            report += f"- Autoremove simulation suggests **{auto_count}** package dependencies are no longer needed.\n\n"
        else:
            report += "- Your package cache is clean. No orphan dependencies detected.\n\n"

        report += "#### 💡 Recommendations\n"
        if auto_count > 0:
            report += f"- **Run Autoremove:** Reclaim disk space and clean dependency paths by executing the `apt` cleanup module in the queue.\n"
            report += "- **Purge Old Configurations:** Deleted packages often leave behind configuration files. Run `apt-get purge` on removed packages to clean `/etc` remnants.\n"
        else:
            report += "- Keep packages updated to ensure stable system security patches.\n"

        report += "\n#### ⚠️ Safety Warning\n"
        report += "> [!WARNING]\n"
        report += "> Autoremove is generally safe, but verify that packages listed do not include development library bindings or header packages (`-dev`) that you need for compiling local C/C++ or Python C-extensions.\n"

        report += self._get_footer()
        return {"response": report}

    def _analyze_storage(self, telemetry):
        # Extract estimated savings and module metrics
        savings_match = re.search(r"Total estimated savings: ([\d\.]+) MB", telemetry)
        savings_mb = float(savings_match.group(1)) if savings_match else 0.0
        
        modules = []
        for line in telemetry.splitlines():
            if line.strip().startswith("- Module"):
                modules.append(line.strip())

        report = self._get_header("Reclaimable Storage Analysis")
        
        report += "#### 🔍 Observations\n"
        report += f"- Total estimated reclaimable storage is **{savings_mb:.1f} MB**.\n"
        report += f"- Pending cleanups detected for **{len(modules)}** system components:\n"
        for mod in modules:
            report += f"  {mod}\n"
        report += "\n"

        report += "#### 💡 Recommendations\n"
        if savings_mb > 0:
            report += f"- **Process Queue:** Execute the proposed queue operations via the main dashboard. Enqueueing them will reclaim approximately `{savings_mb:.1f} MB` of storage.\n"
            if savings_mb > 1000:
                report += "- **High Storage Reclaim:** Over 1 GB of reclaimable space detected. Performing cleanup will significantly improve disk efficiency.\n"
        else:
            report += "- No large cleanup items are currently pending approval. Run a fresh **System Scan** to check for new caches.\n"

        report += "\n#### ⚠️ Safety Warning\n"
        report += "> [!IMPORTANT]\n"
        report += "> All actions enqueued support one-click rollback restoration. However, ensuring current terminal sessions are closed before cleaning local dev caches is advised.\n"

        report += self._get_footer()
        return {"response": report}

    def _generic_advice(self, telemetry):
        report = self._get_header("System Heuristic Scan")
        report += "#### 🔍 Observations\n"
        report += "General system check completed.\n\n"
        report += "#### 💡 Recommendations\n"
        report += "- Perform a full system scan using the **Scan System** button to review potential cache savings.\n"
        report += self._get_footer()
        return {"response": report}
