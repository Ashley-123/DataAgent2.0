import datetime
from typing import List, Optional

from sqlalchemy import and_, select, func, delete, update
from sqlmodel import Session

from apps.template.models.template_prompt_model import TemplatePrompt, TemplatePromptInfo, TemplatePromptTypeEnum


def page_template_prompt(
    session: Session,
    current_page: int,
    page_size: int,
    oid: int,
    type: Optional[str] = None,
    name: Optional[str] = None,
    datasource_id: Optional[int] = None
):
    """分页查询模板提示词"""
    query = select(TemplatePrompt).where(TemplatePrompt.oid == oid)
    
    if type:
        query = query.where(TemplatePrompt.type == type)
    
    if name and name.strip():
        query = query.where(TemplatePrompt.name.ilike(f"%{name.strip()}%"))
    
    if datasource_id is not None:
        query = query.where(
            (TemplatePrompt.datasource_id == datasource_id) | 
            (TemplatePrompt.datasource_id.is_(None))
        )
    
    # 获取总数
    count_query = select(func.count()).select_from(query.subquery())
    total_count = session.exec(count_query).scalar_one()
    
    # 分页
    offset = (current_page - 1) * page_size
    query = query.order_by(TemplatePrompt.create_time.desc()).offset(offset).limit(page_size)
    
    results = session.exec(query).all()
    total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 0
    
    return current_page, page_size, total_count, total_pages, list(results)


def create_template_prompt(
    session: Session,
    info: TemplatePromptInfo,
    oid: int,
    trans
):
    """创建模板提示词"""
    now = datetime.datetime.now()
    
    template_prompt = TemplatePrompt(
        oid=oid,
        type=info.type,
        name=info.name,
        content=info.content,
        datasource_id=info.datasource_id,
        enabled=info.enabled if info.enabled is not None else True,
        create_time=now,
        update_time=now
    )
    
    session.add(template_prompt)
    session.flush()
    session.refresh(template_prompt)
    session.commit()
    
    return template_prompt


def update_template_prompt(
    session: Session,
    info: TemplatePromptInfo,
    oid: int,
    trans
):
    """更新模板提示词"""
    template_prompt = session.get(TemplatePrompt, info.id)
    if not template_prompt:
        raise ValueError(f"Template prompt with id {info.id} not found")
    
    if template_prompt.oid != oid:
        raise ValueError("No permission to update this template prompt")
    
    now = datetime.datetime.now()
    
    template_prompt.type = info.type
    template_prompt.name = info.name
    template_prompt.content = info.content
    template_prompt.datasource_id = info.datasource_id
    template_prompt.enabled = info.enabled if info.enabled is not None else True
    template_prompt.update_time = now
    
    session.add(template_prompt)
    session.flush()
    session.refresh(template_prompt)
    session.commit()
    
    return template_prompt


def delete_template_prompt(
    session: Session,
    id_list: List[int],
    oid: int
):
    """删除模板提示词"""
    stmt = delete(TemplatePrompt).where(
        and_(
            TemplatePrompt.id.in_(id_list),
            TemplatePrompt.oid == oid
        )
    )
    session.exec(stmt)
    session.commit()


def enable_template_prompt(
    session: Session,
    id: int,
    enabled: bool,
    oid: int,
    trans
):
    """启用/禁用模板提示词"""
    template_prompt = session.get(TemplatePrompt, id)
    if not template_prompt:
        raise ValueError(f"Template prompt with id {id} not found")
    
    if template_prompt.oid != oid:
        raise ValueError("No permission to update this template prompt")
    
    template_prompt.enabled = enabled
    template_prompt.update_time = datetime.datetime.now()
    
    session.add(template_prompt)
    session.flush()
    session.refresh(template_prompt)
    session.commit()
    
    return template_prompt


def get_template_prompt_by_id(
    session: Session,
    id: int,
    oid: int
) -> Optional[TemplatePrompt]:
    """根据ID获取模板提示词"""
    template_prompt = session.get(TemplatePrompt, id)
    if template_prompt and template_prompt.oid == oid:
        return template_prompt
    return None


def get_template_prompts_by_type(
    session: Session,
    type: str,
    oid: int,
    datasource_id: Optional[int] = None
) -> List[TemplatePrompt]:
    """根据类型获取启用的模板提示词列表"""
    query = select(TemplatePrompt).where(
        and_(
            TemplatePrompt.type == type,
            TemplatePrompt.oid == oid,
            TemplatePrompt.enabled == True
        )
    )
    
    # 如果指定了数据源ID，优先返回匹配的，否则返回通用的（datasource_id为None）
    if datasource_id is not None:
        query = query.where(
            (TemplatePrompt.datasource_id == datasource_id) | 
            (TemplatePrompt.datasource_id.is_(None))
        )
        # 排序：先返回匹配数据源的，再返回通用的
        # 使用条件排序：有 datasource_id 的排在前面，NULL 排在后面
        from sqlalchemy import case
        query = query.order_by(
            case(
                (TemplatePrompt.datasource_id.isnot(None), 0),
                else_=1
            ),
            TemplatePrompt.datasource_id.desc()
        )
    else:
        # 如果没有指定数据源，只返回通用的
        query = query.where(TemplatePrompt.datasource_id.is_(None))
    
    results = session.exec(query).all()
    return list(results)

