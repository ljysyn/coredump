"""
文件工具模块

提供文件读写和大小控制功能
"""
from pathlib import Path
from typing import Optional


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def read_file(file_path: str, encoding: str = "utf-8") -> str:
        """
        读取文件内容
        
        Args:
            file_path: 文件路径
            encoding: 文件编码
        
        Returns:
            文件内容
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    
    @staticmethod
    def write_file(
        file_path: str,
        content: str,
        encoding: str = "utf-8",
        max_size_mb: Optional[int] = None,
    ) -> bool:
        """
        写入文件内容
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 文件编码
            max_size_mb: 文件最大大小（MB），None表示不限制
        
        Returns:
            是否成功写入完整内容
        """
        path = Path(file_path)
        
        # 创建父目录
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 检查大小限制
        if max_size_mb is not None:
            content_bytes = content.encode(encoding)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            if len(content_bytes) > max_size_bytes:
                # 截断内容
                truncated_bytes = content_bytes[:max_size_bytes]
                with open(path, "wb") as f:
                    f.write(truncated_bytes)
                return False
        
        # 写入完整内容
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        
        return True
    
    @staticmethod
    def check_size_limit(file_path: str, max_size_mb: int) -> bool:
        """
        检查文件大小是否超限
        
        Args:
            file_path: 文件路径
            max_size_mb: 最大大小（MB）
        
        Returns:
            是否在限制内
        """
        path = Path(file_path)
        
        if not path.exists():
            return True
        
        size_bytes = path.stat().st_size
        max_size_bytes = max_size_mb * 1024 * 1024
        
        return size_bytes <= max_size_bytes
    
    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        """
        获取文件大小（MB）
        
        Args:
            file_path: 文件路径
        
        Returns:
            文件大小（MB）
        """
        path = Path(file_path)
        
        if not path.exists():
            return 0.0
        
        size_bytes = path.stat().st_size
        return size_bytes / (1024 * 1024)