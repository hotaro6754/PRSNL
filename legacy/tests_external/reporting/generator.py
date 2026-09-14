import os
import xml.etree.ElementTree as ET
from pathlib import Path
import json

def parse_junit_xml(xml_path):
    if not os.path.exists(xml_path):
        return None
    tree = ET.parse(xml_path)
    root = tree.getroot()
    # Handle single testsuite or testsuites
    if root.tag == 'testsuites':
        testsuites = root.findall('testsuite')
    else:
        testsuites = [root]
        
    tests = 0
    failures = 0
    errors = 0
    skipped = 0
    time = 0.0
    cases = []
    
    for ts in testsuites:
        tests += int(ts.get('tests', 0))
        failures += int(ts.get('failures', 0))
        errors += int(ts.get('errors', 0))
        skipped += int(ts.get('skipped', 0))
        time += float(ts.get('time', 0.0))
        
        for tc in ts.findall('testcase'):
            case_name = tc.get('name')
            case_time = tc.get('time')
            status = 'PASS'
            if tc.find('failure') is not None:
                status = 'FAIL'
            elif tc.find('error') is not None:
                status = 'ERROR'
            elif tc.find('skipped') is not None:
                status = 'SKIP'
            cases.append({'name': case_name, 'status': status, 'time': case_time})
            
    return {
        'tests': tests,
        'failures': failures,
        'errors': errors,
        'skipped': skipped,
        'time': time,
        'cases': cases
    }

def generate_mermaid_pie(passed, failed, skipped):
    return f"""```mermaid
pie title Test Results
    "Passed" : {passed}
    "Failed" : {failed}
    "Skipped" : {skipped}
```"""

def generate_report(category, xml_file, output_file):
    data = parse_junit_xml(xml_file)
    if not data:
        with open(output_file, 'w') as f:
            f.write(f"# {category.capitalize()} Report\n\nNo test data found.\n")
        return
        
    passed = data['tests'] - data['failures'] - data['errors'] - data['skipped']
    
    md = f"# {category.capitalize()} Report\n\n"
    md += f"**Total Tests:** {data['tests']}  \n"
    md += f"**Passed:** {passed}  \n"
    md += f"**Failed:** {data['failures']}  \n"
    md += f"**Errors:** {data['errors']}  \n"
    md += f"**Skipped:** {data['skipped']}  \n"
    md += f"**Total Time:** {data['time']:.2f}s\n\n"
    
    md += generate_mermaid_pie(passed, data['failures'] + data['errors'], data['skipped']) + "\n\n"
    
    md += "## Test Cases\n\n"
    md += "| Test Name | Status | Time |\n"
    md += "|-----------|--------|------|\n"
    for case in data['cases']:
        md += f"| {case['name']} | {case['status']} | {case['time']}s |\n"
        
    with open(output_file, 'w') as f:
        f.write(md)
    print(f"Generated {output_file}")

def generate_all_reports():
    audit_dir = Path("artifacts/audit")
    reports_dir = Path("artifacts/reports")
    reports_dir.mkdir(exist_ok=True, parents=True)
    
    categories = ["core_integrity", "detection", "security", "resilience", "performance", "e2e", "independent_verification"]
    
    for cat in categories:
        xml_file = audit_dir / f"{cat}_results.xml"
        out_file = reports_dir / f"{cat}_report.md"
        generate_report(cat, xml_file, out_file)
        
    print("All reports generated successfully in artifacts/reports")

if __name__ == '__main__':
    generate_all_reports()
