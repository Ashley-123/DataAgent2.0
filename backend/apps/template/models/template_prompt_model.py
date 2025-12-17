from datetime import datetime
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel
from sqlalchemy import Column, Text, BigInteger, DateTime, String
from sqlmodel import SQLModel, Field


class TemplatePromptTypeEnum(str, Enum):
    """模板提示词类型枚举"""
    SQL = "sql"  # SQL生成
    CHART = "chart"  # 图表生成
    ANALYSIS = "analysis"  # 数据分析
    PREDICT = "predict"  # 数据预测
    GUESS = "guess"  # 推荐问题
    DATASOURCE = "datasource"  # 数据源选择
    PERMISSIONS = "permissions"  # 权限过滤
    DYNAMIC_SQL = "dynamic_sql"  # 动态SQL


class TemplatePrompt(SQLModel, table=True):
    """用户自定义系统提示词表"""
    __tablename__ = "template_prompt"
    
    id: Optional[int] = Field(sa_column=Column(BigInteger, primary_key=True))
    oid: Optional[int] = Field(sa_column=Column(BigInteger, nullable=True, default=1))
    type: Optional[str] = Field(sa_column=Column(String(50), nullable=False), description="提示词类型")
    name: Optional[str] = Field(sa_column=Column(String(255), nullable=True), description="提示词名称")
    content: Optional[str] = Field(sa_column=Column(Text, nullable=False), description="提示词内容")
    datasource_id: Optional[int] = Field(sa_column=Column(BigInteger, nullable=True), description="关联的数据源ID，为空表示适用于所有数据源")
    enabled: Optional[bool] = Field(default=True, description="是否启用")
    create_time: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=False), nullable=True))
    update_time: Optional[datetime] = Field(sa_column=Column(DateTime(timezone=False), nullable=True))


class TemplatePromptInfo(BaseModel):
    """模板提示词信息模型"""
    id: Optional[int] = None
    type: str
    name: Optional[str] = None
    content: str
    datasource_id: Optional[int] = None
    enabled: Optional[bool] = True
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

