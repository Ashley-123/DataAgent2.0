from typing import Optional
from sqlmodel import Session

from apps.template.curd.template_prompt import get_template_prompts_by_type


def get_user_template_prompts(
    session: Session,
    type: str,
    oid: int,
    datasource_id: Optional[int] = None
) -> str:
    """
    获取用户自定义模板提示词并合并为字符串
    
    Args:
        session: 数据库会话
        type: 提示词类型 (sql, chart, analysis, predict, guess, datasource, permissions, dynamic_sql)
        oid: 组织ID
        datasource_id: 数据源ID（可选）
    
    Returns:
        合并后的用户自定义提示词字符串，如果没有则返回空字符串
    """
    prompts = get_template_prompts_by_type(session, type, oid, datasource_id)
    
    if not prompts:
        return ""
    
    # 合并所有启用的提示词，用换行符分隔
    prompt_contents = []
    for prompt in prompts:
        if prompt.content and prompt.content.strip():
            prompt_contents.append(prompt.content.strip())
    
    if prompt_contents:
        # 在原有custom_prompt的基础上追加用户自定义提示词
        return "\n\n" + "\n\n".join(prompt_contents)
    
    return ""

