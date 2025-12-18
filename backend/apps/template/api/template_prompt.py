from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from apps.template.curd.template_prompt import (
    page_template_prompt,
    create_template_prompt,
    update_template_prompt,
    delete_template_prompt,
    enable_template_prompt,
    get_template_prompt_by_id
)
from apps.template.models.template_prompt_model import TemplatePromptInfo
from common.core.deps import SessionDep, CurrentUser, Trans

router = APIRouter(tags=["Template Prompt"], prefix="/system/template-prompt")


@router.get("/page/{current_page}/{page_size}")
async def pager(
    session: SessionDep,
    current_user: CurrentUser,
    current_page: int,
    page_size: int,
    type: Optional[str] = Query(None, description="提示词类型(可选)"),
    name: Optional[str] = Query(None, description="搜索提示词名称(可选)"),
    datasource_id: Optional[int] = Query(None, description="数据源ID(可选)")
):
    """分页查询模板提示词"""
    current_page, page_size, total_count, total_pages, _list = page_template_prompt(
        session=session,
        current_page=current_page,
        page_size=page_size,
        oid=current_user.oid,
        type=type,
        name=name,
        datasource_id=datasource_id
    )

    # 将 SQLModel 对象列表转换为字典列表，确保正确序列化
    data_list = []
    for item in _list:
        # 尝试多种方式提取数据
        item_dict = {}
        try:
            # 方法1: 尝试使用 model_dump（SQLModel 对象）
            if hasattr(item, 'model_dump'):
                item_dict = item.model_dump()
            # 方法2: 尝试直接访问属性
            else:
                item_dict = {
                    "id": item.id if hasattr(item, 'id') else None,
                    "oid": item.oid if hasattr(item, 'oid') else None,
                    "type": item.type if hasattr(item, 'type') else None,
                    "name": item.name if hasattr(item, 'name') else None,
                    "content": item.content if hasattr(item, 'content') else None,
                    "datasource_id": item.datasource_id if hasattr(item, 'datasource_id') else None,
                    "enabled": item.enabled if hasattr(item, 'enabled') else None,
                    "create_time": item.create_time if hasattr(item, 'create_time') else None,
                    "update_time": item.update_time if hasattr(item, 'update_time') else None
                }
        except (AttributeError, KeyError, TypeError) as e:
            # 方法3: 如果以上都失败，尝试使用 getattr
            try:
                item_dict = {
                    "id": getattr(item, 'id', None),
                    "oid": getattr(item, 'oid', None),
                    "type": getattr(item, 'type', None),
                    "name": getattr(item, 'name', None),
                    "content": getattr(item, 'content', None),
                    "datasource_id": getattr(item, 'datasource_id', None),
                    "enabled": getattr(item, 'enabled', None),
                    "create_time": getattr(item, 'create_time', None),
                    "update_time": getattr(item, 'update_time', None)
                }
            except Exception:
                # 如果还是失败，返回空字典（不应该发生）
                item_dict = {}
        
        data_list.append(TemplatePromptInfo.model_validate(item_dict))

    return {
        "current_page": current_page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "data": data_list
    }


@router.put("")
async def create_or_update(
    session: SessionDep,
    current_user: CurrentUser,
    trans: Trans,
    info: TemplatePromptInfo
):
    """创建或更新模板提示词"""
    oid = current_user.oid
    if info.id:
        result = update_template_prompt(session, info, oid, trans)
    else:
        result = create_template_prompt(session, info, oid, trans)
    
    # 手动构建字典，确保所有字段都被正确提取
    result_dict = {
        "id": result.id,
        "oid": result.oid,
        "type": result.type,
        "name": result.name,
        "content": result.content,
        "datasource_id": result.datasource_id,
        "enabled": result.enabled,
        "create_time": result.create_time,
        "update_time": result.update_time
    }
    return TemplatePromptInfo.model_validate(result_dict)


@router.delete("")
async def delete(
    session: SessionDep,
    current_user: CurrentUser,
    id_list: list[int]
):
    """删除模板提示词"""
    delete_template_prompt(session, id_list, current_user.oid)


@router.get("/{id}/enable/{enabled}")
async def enable(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    enabled: bool,
    trans: Trans
):
    """启用/禁用模板提示词"""
    result = enable_template_prompt(session, id, enabled, current_user.oid, trans)
    # 手动构建字典，确保所有字段都被正确提取
    result_dict = {
        "id": result.id,
        "oid": result.oid,
        "type": result.type,
        "name": result.name,
        "content": result.content,
        "datasource_id": result.datasource_id,
        "enabled": result.enabled,
        "create_time": result.create_time,
        "update_time": result.update_time
    }
    return TemplatePromptInfo.model_validate(result_dict)


@router.get("/{id}")
async def get_by_id(
    session: SessionDep,
    current_user: CurrentUser,
    id: int
):
    """根据ID获取模板提示词"""
    template_prompt = get_template_prompt_by_id(session, id, current_user.oid)
    if not template_prompt:
        raise HTTPException(status_code=404, detail="Template prompt not found")
    # 手动构建字典，确保所有字段都被正确提取
    result_dict = {
        "id": template_prompt.id,
        "oid": template_prompt.oid,
        "type": template_prompt.type,
        "name": template_prompt.name,
        "content": template_prompt.content,
        "datasource_id": template_prompt.datasource_id,
        "enabled": template_prompt.enabled,
        "create_time": template_prompt.create_time,
        "update_time": template_prompt.update_time
    }
    return TemplatePromptInfo.model_validate(result_dict)

