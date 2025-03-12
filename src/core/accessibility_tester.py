import os
import json
import subprocess
import tempfile
import shutil
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import requests

from ..core.base_tester import BaseAccessibilityTester

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AccessibilityTool")


class AccessibilityTestRunner:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r") as f:
            self.config = json.load(f)
        self.standards = self.config.get("standards", ["WCAG2AA"])
        self.timeout = self.config.get("timeout", 120000)
        self.tools = [AxeTester(self.standards), WaveTester(), Pa11yTester(self.standards)]

    def run_tests(self, url):
        with ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda tester: tester.test_accessibility(url), self.tools))
        summary = self.generate_summary(results)
        self.save_summary(summary)
        return results

    def generate_summary(self, results):
        return {
            "total_issues": sum(r["summary"]["total"] for r in results),
            "errors": sum(r["summary"]["errors"] for r in results),
            "warnings": sum(r["summary"]["warnings"] for r in results),
        }

    def save_summary(self, summary, output_path="summary.json"):
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)


class AxeTester(BaseAccessibilityTester):
    def __init__(self, standards):
        super().__init__("axe")
        self.standards = standards

    def test_accessibility(self, url):
        axe_script = f"""
        return axe.run(document, {{
            runOnly: {json.dumps(self.standards)}
        }});
        """
        return self.execute_js_test(url, axe_script)


class WaveTester(BaseAccessibilityTester):
    def test_accessibility(self, url):
        response = requests.get(f"https://wave.webaim.org/api/request?url={url}&key=YOUR_API_KEY")
        return response.json() if response.status_code == 200 else {}


class Pa11yTester(BaseAccessibilityTester):
    def __init__(self, standards):
        super().__init__("pa11y")
        self.standards = standards

    def test_accessibility(self, url):
        cmd = ["pa11y", url, "--standard", self.standards[0], "--timeout", str(self.timeout)]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        return json.loads(result.stdout) if result.returncode == 0 else {}


if __name__ == "__main__":
    test_runner = AccessibilityTestRunner()
    test_results = test_runner.run_tests("https://www.sony.es")
    print(json.dumps(test_results, indent=2))
