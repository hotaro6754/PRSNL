"""
Patch /api/stats in backend/main.py to return the keys expected by health/page.tsx
"""
import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will find the return statement of get_stats
pattern = r'(return \{\n\s*"environment": ENVIRONMENT\.value,.*?"detection_latency_ms": random\.randint\(12, 45\)\n\s*\})'
match = re.search(pattern, content, re.DOTALL)
if match:
    old_return = match.group(1)
    
    new_return = """return {
        "environment": ENVIRONMENT.value,
        "active_cases": active,
        "critical_cases": critical,
        "active": active,
        "critical": critical,
        "uptime": uptime,
        "processed_eps": processed_eps,
        "alerts_per_min": round(ALERTS_GENERATED._value.get() / (uptime / 60), 2),
        "flows_processed": FLOWS_PROCESSED._value.get(),
        "ml_inferences": telemetry["total_ml_inferences"],
        "feature_windows": telemetry["total_feature_windows"],
        "throughput_fps": processed_eps,
        "offered_eps": processed_eps + (lag / 5.0),
        "consumer_lag": lag,
        "detection_latency_ms": random.randint(12, 45)
    }"""
    
    content = content.replace(old_return, new_return)
    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Patched /api/stats to include ui required keys.")
else:
    print("Could not find the return dict in get_stats!")
