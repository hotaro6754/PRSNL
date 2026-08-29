import pytest
import os
from pathlib import Path
import json

def test_report_integrity_001_invalid_case_id():
    # Test that invalid case ID or missing data is handled safely
    from tests_external.reporting.generator import parse_junit_xml
    
    # Passing a non-existent file
    result = parse_junit_xml("artifacts/audit/non_existent.xml")
    assert result is None, "Should gracefully return None for invalid/missing XML"

def test_report_generation_blackbox():
    # Verify report generation creates .md files
    from tests_external.reporting.generator import generate_all_reports
    
    # Ensure audit directory exists
    Path("artifacts/audit").mkdir(exist_ok=True, parents=True)
    # Write a dummy xml to test parsing and generation
    dummy_xml = """<?xml version="1.0" encoding="utf-8"?>
<testsuites>
    <testsuite tests="2" failures="1" errors="0" skipped="0" time="1.5">
        <testcase name="test_security_headers" time="0.5"/>
        <testcase name="test_invalid_auth" time="1.0">
            <failure message="Auth failed"/>
        </testcase>
    </testsuite>
</testsuites>"""
    with open("artifacts/audit/core_integrity_results.xml", "w") as f:
        f.write(dummy_xml)
        
    generate_all_reports()
    
    assert os.path.exists("artifacts/reports/core_integrity_report.md")
    
    with open("artifacts/reports/core_integrity_report.md", "r") as f:
        content = f.read()
        assert "Total Tests:** 2" in content
        assert "Failed:** 1" in content
        assert "Passed:** 1" in content
        assert "```mermaid" in content
