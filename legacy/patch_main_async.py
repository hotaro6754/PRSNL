import re

def patch_main_async():
    with open('backend/main.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update process_pcap_background (adding tenant_id)
    # Original: def process_pcap_background(filename: str, loop: asyncio.AbstractEventLoop):
    pcap_orig = r"def process_pcap_background\(filename: str, loop: asyncio\.AbstractEventLoop\):"
    pcap_new = r"def process_pcap_background(filename: str, loop: asyncio.AbstractEventLoop, tenant_id: str = 'default_org'):"
    content = re.sub(pcap_orig, pcap_new, content)
    
    # 2. Inject tenant_id into adapter.consume() in process_pcap_background
    adapter_orig = r"for flow in adapter\.consume\(filename\):"
    adapter_new = r"""for flow in adapter.consume(filename):
            flow.organization_id = tenant_id"""
    content = re.sub(adapter_orig, adapter_new, content)

    # 3. Update ready_windows loop
    # Original: for wid, src_ip, window_flows in ready_windows:
    #           asyncio.run_coroutine_threadsafe(process_window(wid, src_ip, window_flows), loop)
    rw_orig = r"for wid, src_ip, window_flows in ready_windows:"
    rw_new = r"for wid, src_ip, org_id, window_flows in ready_windows:"
    content = re.sub(rw_orig, rw_new, content)
    
    pw_orig1 = r"asyncio\.run_coroutine_threadsafe\(process_window\(wid, src_ip, window_flows\), loop\)"
    pw_new1 = r"asyncio.run_coroutine_threadsafe(process_window(wid, src_ip, window_flows, org_id), loop)"
    content = re.sub(pw_orig1, pw_new1, content)
    
    # 4. Update final_windows loop
    fw_orig = r"for wid, src_ip, window_flows in final_windows:"
    fw_new = r"for wid, src_ip, org_id, window_flows in final_windows:"
    content = re.sub(fw_orig, fw_new, content)

    # 5. Update process_window signature
    pw_sig_orig = r"async def process_window\(wid: int, src_ip: str, window_flows: List\[NetworkObservation\]\):"
    pw_sig_new = r"async def process_window(wid: int, src_ip: str, window_flows: List[NetworkObservation], org_id: str = 'default_org'):"
    content = re.sub(pw_sig_orig, pw_sig_new, content)
    
    # 6. Inside process_window, patch det_alerts to append org_id
    # det_alerts.extend(detector.evaluate_window(window_flows, wid))
    # We'll just patch the Fusion engine or where the alert is added to the queue
    # 4. Evidence fusion
    fuse_orig = r"final_alerts = fusion_engine\.fuse\(det_alerts, ml_pred, window_flows\[0\]\)\n\s+for alert in final_alerts:\n\s+await alert_queue\.put\(alert\)"
    fuse_new = r"""final_alerts = fusion_engine.fuse(det_alerts, ml_pred, window_flows[0])
        for alert in final_alerts:
            alert.organization_id = org_id
            if alert.evidence:
                for ev in alert.evidence:
                    ev.organization_id = org_id
            await alert_queue.put(alert)"""
    content = re.sub(fuse_orig, fuse_new, content)

    # 7. Also update start_replay to pass tenant_id
    # async def start_replay(request: ReplayRequest, background_tasks: BackgroundTasks):
    replay_orig = r"async def start_replay\(request: ReplayRequest, background_tasks: BackgroundTasks\):"
    replay_new = r"async def start_replay(request: ReplayRequest, background_tasks: BackgroundTasks, tenant_id: str = Depends(get_current_tenant)):"
    content = re.sub(replay_orig, replay_new, content)
    
    add_task_orig = r"background_tasks\.add_task\(process_pcap_background, request\.filename, loop\)"
    add_task_new = r"background_tasks.add_task(process_pcap_background, request.filename, loop, tenant_id)"
    content = re.sub(add_task_orig, add_task_new, content)

    with open('backend/main.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("main.py async data plane patched!")

patch_main_async()
