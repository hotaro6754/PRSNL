from abc import ABC, abstractmethod
from typing import List, Optional, Any
from backend.contracts.alert import Alert
from backend.contracts.case import SecurityCase

class BaseRepository(ABC):
    """
    Persistence boundary. Repositories handle long-term storage of cases and alerts.
    The high-speed streaming plane does NOT write every packet or flow here.
    """
    
    @abstractmethod
    def save_alert(self, alert: Alert) -> None:
        pass
        
    @abstractmethod
    def save_case(self, case: SecurityCase) -> None:
        pass
        
    @abstractmethod
    def get_active_cases(self) -> List[SecurityCase]:
        pass
