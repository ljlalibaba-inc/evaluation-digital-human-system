#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent基类
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Agent基类"""
    
    def __init__(self, name: str, config: Dict = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    def execute(self, input_data: Any) -> Any:
        """执行Agent任务"""
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        """验证输入数据"""
        return True
    
    def log(self, message: str):
        """记录日志"""
        print(f"[{self.name}] {message}")
