import re

with open('backend/main.py', 'r') as f:
    code = f.read()

# Add WindowManager imports
import_statement = \"\"\"
from backend.streaming.window_manager import WindowManager
from backend.contracts.observation import NetworkObservation
\"\"\"
if "WindowManager" not in code:
    code = code.replace("from backend.ml.router import ModelRouter", "from backend.ml.router import ModelRouter" + import_statement)

# Initialize WindowManager
if "window_manager =" not in code:
    code = code.replace("feature_engine = TumblingWindowFeatureEngine()", "feature_engine = TumblingWindowFeatureEngine()\nwindow_manager = WindowManager(window_size_ms=10000, allowed_lateness_ms=2000)")

# Create process_window function
process_window_func = \"\"\"
async def process_window(wid: int, src_ip: str, window_flows: List[NetworkObservation]):
    telemetry["total_feature_windows"] += 1
    
    # 1. Deterministic detection
    det_alerts = []
    for detector in detectors:
        det_alerts.extend(detector.evaluate_window(window_flows, wid))
        
    # 2. Feature extraction
    fv = feature_engine.extract_features(window_flows)
    
    # 3. ML inference
    ml_pred = None
    if fv is not None:
        # Use first flow for flow context in fusion
        flow = window_flows[0]
        ml_pred = model_router.evaluate(fv, flow)
        if ml_pred is not None:
            telemetry["total_ml_inferences"] += 1
            ML_INFERENCES.inc()
            try:
                await mongo.save_prediction(ml_pred.model_dump(mode="json"))
            except Exception:
                pass

    # 4. Evidence fusion
    if len(window_flows) > 0:
        final_alerts = fusion_engine.fuse(det_alerts, ml_pred, window_flows[0])
        for alert in final_alerts:
            await alert_queue.put(alert)
\"\"\"

if "def process_window" not in code:
    code = code.replace("async def _process_flow(flow):", process_window_func + "\nasync def _process_flow(flow):")

# Rewrite _process_flow
process_flow_new = \"\"\"
async def _process_flow(flow):
    telemetry["total_flows"] += 1
    FLOWS_PROCESSED.inc()
    window_manager.add_observation(flow)
\"\"\"
code = re.sub(r'async def _process_flow\(flow\):.*?#  PCAP Replay ', process_flow_new + '\n#  PCAP Replay ', code, flags=re.DOTALL)


# Add the window tick task
tick_task = \"\"\"
async def window_tick_task():
    logger.info("Starting WindowManager live tick task...")
    while True:
        try:
            now_ms = int(time.time() * 1000)
            ready_windows = window_manager.flush_ready_windows(now_ms, is_live=True)
            for wid, src_ip, window_flows in ready_windows:
                await process_window(wid, src_ip, window_flows)
        except Exception as e:
            logger.error("Error in window tick: %s", e)
        await asyncio.sleep(0.5)
\"\"\"
if "def window_tick_task" not in code:
    code = code.replace("@app.on_event(\"startup\")", tick_task + "\n@app.on_event(\"startup\")")
    code = code.replace("asyncio.create_task(kafka_consumer_task())", "asyncio.create_task(kafka_consumer_task())\n    asyncio.create_task(window_tick_task())")


# Rewrite PCAP loop
pcap_loop_old = r'for flow in adapter.consume\(filename\):.*?for detector in detectors:.*?for alert in detector.flush\(\):.*?asyncio.run_coroutine_threadsafe\(alert_queue.put\(alert\), loop\)'
pcap_loop_new = \"\"\"
        for flow in adapter.consume(filename):
            telemetry["total_flows"] += 1
            FLOWS_PROCESSED.inc()
            window_manager.add_observation(flow)
            
            ready_windows = window_manager.flush_ready_windows(0, is_live=False)
            for wid, src_ip, window_flows in ready_windows:
                asyncio.run_coroutine_threadsafe(process_window(wid, src_ip, window_flows), loop)
                
        # Final flush
        final_windows = window_manager.flush_all()
        for wid, src_ip, window_flows in final_windows:
            asyncio.run_coroutine_threadsafe(process_window(wid, src_ip, window_flows), loop)
\"\"\"
code = re.sub(pcap_loop_old, pcap_loop_new.strip(), code, flags=re.DOTALL)

with open('backend/main.py', 'w') as f:
    f.write(code)
