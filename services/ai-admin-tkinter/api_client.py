"""
API client for AI Engine communication
Handles all HTTP requests with proper error handling and threading
"""

import requests
import threading
from typing import Callable, Optional, Dict, Any
from config import API_BASE_URL, API_TIMEOUT


class AIEngineClient:
    """Async API client for AI Engine"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        
    def get_model_info(self, callback: Callable, error_callback: Optional[Callable] = None):
        """Fetch model information asynchronously"""
        def fetch():
            try:
                response = requests.get(
                    f"{self.base_url}/model-info",
                    timeout=API_TIMEOUT
                )
                response.raise_for_status()
                callback(response.json())
            except Exception as e:
                if error_callback:
                    error_callback(str(e))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def train_model(self, params: Dict[str, Any], callback: Callable, error_callback: Optional[Callable] = None):
        """Train model asynchronously"""
        def train():
            try:
                response = requests.post(
                    f"{self.base_url}/train",
                    json=params,
                    timeout=120
                )
                response.raise_for_status()
                callback(response.json())
            except Exception as e:
                if error_callback:
                    error_callback(str(e))
        
        threading.Thread(target=train, daemon=True).start()
    
    def reset_model(self, callback: Callable, error_callback: Optional[Callable] = None):
        """Reset model asynchronously"""
        def reset():
            try:
                response = requests.post(
                    f"{self.base_url}/reset-model",
                    timeout=API_TIMEOUT
                )
                response.raise_for_status()
                callback(response.json())
            except Exception as e:
                if error_callback:
                    error_callback(str(e))
        
        threading.Thread(target=reset, daemon=True).start()
    
    def upload_dataset(self, file_path: str, callback: Callable, error_callback: Optional[Callable] = None):
        """Upload CSV dataset asynchronously"""
        def upload():
            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (file_path.split('/')[-1].split('\\')[-1], f, 'text/csv')}
                    response = requests.post(
                        f"{self.base_url}/upload-dataset",
                        files=files,
                        timeout=60
                    )
                    response.raise_for_status()
                    callback(response.json())
            except Exception as e:
                if error_callback:
                    error_callback(str(e))
        
        threading.Thread(target=upload, daemon=True).start()
    
    def check_health(self, callback: Callable, error_callback: Optional[Callable] = None):
        """Check API health"""
        def check():
            try:
                response = requests.get(
                    f"{self.base_url}/health",
                    timeout=5
                )
                response.raise_for_status()
                callback(True)
            except Exception as e:
                if error_callback:
                    error_callback(str(e))
                else:
                    callback(False)
        
        threading.Thread(target=check, daemon=True).start()
