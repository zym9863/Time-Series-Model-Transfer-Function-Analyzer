"""
FastAPI客户端库

提供简单易用的Python客户端来调用时间序列分析API
"""

import requests
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin

class TimeSeriesAPIClient:
    """时间序列分析API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        初始化客户端
        
        Args:
            base_url: API服务基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送HTTP请求"""
        url = urljoin(self.api_base + "/", endpoint.lstrip('/'))
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return self._make_request("GET", "/health")
    
    def get_supported_models(self) -> Dict[str, Any]:
        """获取支持的模型类型"""
        return self._make_request("GET", "/models")
    
    def validate_model_string(self, model_string: str) -> Dict[str, Any]:
        """验证模型字符串"""
        return self._make_request("GET", f"/models/validate/{model_string}")
    
    def analyze_arima(self, 
                     p: int, d: int, q: int,
                     ar_params: Optional[List[float]] = None,
                     ma_params: Optional[List[float]] = None,
                     constant: float = 0.0,
                     name: Optional[str] = None,
                     include_stability: bool = True,
                     include_impulse: bool = False,
                     include_frequency: bool = False,
                     max_lag: int = 20,
                     frequencies: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        分析ARIMA模型
        
        Args:
            p: 自回归阶数
            d: 差分阶数
            q: 移动平均阶数
            ar_params: 自回归参数
            ma_params: 移动平均参数
            constant: 常数项
            name: 模型名称
            include_stability: 是否包含稳定性分析
            include_impulse: 是否包含脉冲响应
            include_frequency: 是否包含频率响应
            max_lag: 脉冲响应最大滞后
            frequencies: 频率列表
            
        Returns:
            分析结果
        """
        data = {
            "p": p, "d": d, "q": q,
            "ar_params": ar_params,
            "ma_params": ma_params,
            "constant": constant,
            "name": name,
            "include_stability": include_stability,
            "include_impulse": include_impulse,
            "include_frequency": include_frequency,
            "max_lag": max_lag,
            "frequencies": frequencies
        }
        return self._make_request("POST", "/analyze/arima", json=data)
    
    def analyze_sarima(self,
                      p: int, d: int, q: int,
                      P: int, D: int, Q: int, m: int,
                      ar_params: Optional[List[float]] = None,
                      ma_params: Optional[List[float]] = None,
                      seasonal_ar_params: Optional[List[float]] = None,
                      seasonal_ma_params: Optional[List[float]] = None,
                      constant: float = 0.0,
                      name: Optional[str] = None,
                      include_stability: bool = True,
                      include_impulse: bool = False,
                      include_frequency: bool = False,
                      max_lag: int = 20,
                      frequencies: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        分析SARIMA模型
        
        Args:
            p, d, q: 非季节性ARIMA参数
            P, D, Q, m: 季节性参数
            ar_params: 自回归参数
            ma_params: 移动平均参数
            seasonal_ar_params: 季节性自回归参数
            seasonal_ma_params: 季节性移动平均参数
            constant: 常数项
            name: 模型名称
            include_stability: 是否包含稳定性分析
            include_impulse: 是否包含脉冲响应
            include_frequency: 是否包含频率响应
            max_lag: 脉冲响应最大滞后
            frequencies: 频率列表
            
        Returns:
            分析结果
        """
        data = {
            "p": p, "d": d, "q": q,
            "P": P, "D": D, "Q": Q, "m": m,
            "ar_params": ar_params,
            "ma_params": ma_params,
            "seasonal_ar_params": seasonal_ar_params,
            "seasonal_ma_params": seasonal_ma_params,
            "constant": constant,
            "name": name,
            "include_stability": include_stability,
            "include_impulse": include_impulse,
            "include_frequency": include_frequency,
            "max_lag": max_lag,
            "frequencies": frequencies
        }
        return self._make_request("POST", "/analyze/sarima", json=data)
    
    def analyze_model_string(self,
                           model_string: str,
                           include_stability: bool = True,
                           include_impulse: bool = False,
                           include_frequency: bool = False,
                           max_lag: int = 20,
                           frequencies: Optional[List[float]] = None) -> Dict[str, Any]:
        """
        通过模型字符串分析
        
        Args:
            model_string: 模型字符串
            include_stability: 是否包含稳定性分析
            include_impulse: 是否包含脉冲响应
            include_frequency: 是否包含频率响应
            max_lag: 脉冲响应最大滞后
            frequencies: 频率列表
            
        Returns:
            分析结果
        """
        data = {
            "model_string": model_string,
            "include_stability": include_stability,
            "include_impulse": include_impulse,
            "include_frequency": include_frequency,
            "max_lag": max_lag,
            "frequencies": frequencies
        }
        return self._make_request("POST", "/analyze/model-string", json=data)
    
    def get_transfer_function(self, model_string: str) -> Dict[str, Any]:
        """仅获取传递函数"""
        return self._make_request("GET", f"/analyze/transfer-function/{model_string}")
    
    def get_stability_analysis(self, model_string: str) -> Dict[str, Any]:
        """仅获取稳定性分析"""
        return self._make_request("GET", f"/analyze/stability/{model_string}")

# 便捷函数
def create_client(base_url: str = "http://localhost:8000") -> TimeSeriesAPIClient:
    """创建API客户端实例"""
    return TimeSeriesAPIClient(base_url)
