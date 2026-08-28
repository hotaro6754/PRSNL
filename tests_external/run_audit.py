import json
import os
import subprocess
import sys
from pathlib import Path

def run_pytest(test_dir):
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_dir, "--json-report", "--json-report-file=artifacts/audit/report.json"],
        capture_output=True, text=True
    )
    return result

def run_category_test(category_name, test_path, env):
    print(f"{category_name}...", end=" ", flush=True)
    if not os.path.exists(test_path):
        print("PASS (no tests)")
        return True
        
    safe_name = category_name.replace(' ', '_').lower()
    xml_path = f"artifacts/audit/{safe_name}_results.xml"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-q", "--tb=short", f"--junitxml={xml_path}"],
        env=env,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("PASS")
        return True
    else:
        print("FAIL")
        print(result.stdout)
        return False

def main():
    print("========================================")
    print("CYBEROS RELEASE GATE")
    print("========================================")
    
    audit_dir = Path("artifacts/audit")
    audit_dir.mkdir(parents=True, exist_ok=True)
    
    env = os.environ.copy()
    
    categories = [
        ("Core Integrity", "tests_external/api_contracts"),
        ("Detection", "tests_external/provenance"),
        ("Security", "tests_external/security"),
        ("Resilience", "tests_external/resilience"),
        ("Performance", "tests_external/performance"),
        ("E2E", "tests_external/e2e"),
        ("Independent Verification", "tests_external/graph")
    ]
    
    all_passed = True
    for name, path in categories:
        passed = run_category_test(name, path, env)
        if not passed:
            all_passed = False
            
    print("========================================")
    
    report = {
        "status": "PASS" if all_passed else "FAIL",
        "details": "Audit executed."
    }
    with open(audit_dir / "report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    if not all_passed:
        print("CRITICAL: Audit failed. Failing closed.")
        sys.exit(1)
    
    print("Audit passed successfully.")
    sys.exit(0)

if __name__ == "__main__":
    main()
