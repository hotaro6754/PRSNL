import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
from backend.contracts.observation import NetworkObservation

class WindowManager:
    """
    Explicit WindowManager that separates event time from processing time.
    Maintains window lifecycle: open, active, closing, closed.
    """
    def __init__(self, window_size_ms: int = 10000, allowed_lateness_ms: int = 2000):
        self.window_size_ms = window_size_ms
        self.allowed_lateness_ms = allowed_lateness_ms
        # Keyed by (window_id, source_ip)
        self.windows: Dict[tuple, List[NetworkObservation]] = defaultdict(list)
        self.latest_event_time_ms: int = 0
        
    def _get_window_id(self, timestamp_ms: int) -> int:
        return (timestamp_ms // self.window_size_ms) * self.window_size_ms

    def add_observation(self, obs: NetworkObservation):
        ts = obs.timestamp
        if ts > self.latest_event_time_ms:
            self.latest_event_time_ms = ts
            
        wid = self._get_window_id(ts)
        self.windows[(wid, obs.source_ip, getattr(obs, "organization_id", "default_org"))].append(obs)

    def flush_ready_windows(self, current_wall_time_ms: int, is_live: bool = True) -> List[tuple]:
        """
        Returns windows that are eligible for closure and deletes them from active tracking.
        """
        ready = []
        keys_to_delete = []
        for key in list(self.windows.keys()):
            wid, src_ip, org_id = key
            window_end = wid + self.window_size_ms
            
            ready_by_event = self.latest_event_time_ms >= (window_end + self.allowed_lateness_ms)
            ready_by_wall = False
            if is_live and current_wall_time_ms > 0:
                # If we're operating on real Unix timestamps
                ready_by_wall = current_wall_time_ms >= (window_end + self.allowed_lateness_ms)
                
            if ready_by_event or ready_by_wall:
                ready.append((wid, src_ip, org_id, self.windows[key]))
                keys_to_delete.append(key)
                
        for k in keys_to_delete:
            del self.windows[k]
            
        ready.sort(key=lambda x: x[0])
        return ready

    def flush_all(self) -> List[tuple]:
        """Flushes all remaining windows regardless of time."""
        ready = []
        for key in list(self.windows.keys()):
            wid, src_ip, org_id = key
            ready.append((wid, src_ip, org_id, self.windows[key]))
            
        self.windows.clear()
        ready.sort(key=lambda x: x[0])
        return ready
