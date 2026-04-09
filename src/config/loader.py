"""
配置加载器

支持从YAML文件和环境变量加载配置
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigLoader:
    """配置加载器"""
    
    @staticmethod
    def load_yaml(file_path: str) -> Dict[str, Any]:
        """
        加载YAML配置文件
        
        Args:
            file_path: YAML文件路径
        
        Returns:
            配置字典
        """
        path = Path(file_path)
        
        if not path.exists():
            return {}
        
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    @staticmethod
    def get_env_var(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        获取环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
        
        Returns:
            环境变量值
        """
        return os.getenv(key, default)
    
    @staticmethod
    def get_env_int(key: str, default: int) -> int:
        """
        获取整数类型环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
        
        Returns:
            整数值
        """
        value = os.getenv(key)
        if value is None:
            return default
        
        try:
            return int(value)
        except ValueError:
            return default
    
    @staticmethod
    def override_from_env(config: Dict[str, Any], prefix: str = "COREDUMP_") -> Dict[str, Any]:
        """
        使用环境变量覆盖配置
        
        Args:
            config: 原始配置字典
            prefix: 环境变量前缀
        
        Returns:
            覆盖后的配置字典
        """
        result = config.copy()
        
        # 映射环境变量
        env_mappings = {
            "SSH_TIMEOUT": "ssh_timeout",
            "DEFAULT_TIMEOUT": "default_timeout",
            "REPORT_MAX_SIZE": "report_max_size",
            "LOG_LEVEL": "log_level",
            "LOG_FILE": "log_file",
            "DEVICES_DIR": "devices_dir",
            "REPORTS_DIR": "reports_dir",
        }
        
        for env_key, config_key in env_mappings.items():
            full_key = f"{prefix}{env_key}"
            env_value = os.getenv(full_key)
            
            if env_value is not None:
                result[config_key] = env_value
        
        return result
    
    @staticmethod
    def load_settings(file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        加载设置配置
        
        Args:
            file_path: 配置文件路径，None表示使用默认路径
        
        Returns:
            设置配置字典
        """
        # 默认配置
        default_settings = {
            "ssh_timeout": 10,
            "default_timeout": 30,
            "report_max_size": 100,
            "log_level": "INFO",
            "log_file": "logs/coredump.log",
        }
        
        # 从文件加载
        if file_path:
            file_config = ConfigLoader.load_yaml(file_path)
            default_settings.update(file_config)
        
        # 从环境变量覆盖
        return ConfigLoader.override_from_env(default_settings)