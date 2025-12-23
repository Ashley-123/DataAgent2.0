from typing import Optional

from fastapi import APIRouter, Query, HTTPException

from apps.template.curd.template_prompt import (
    page_template_prompt,
    create_template_prompt,
    update_template_prompt,
    delete_template_prompt,
    enable_template_prompt,
    get_template_prompt_by_id,
    get_template_prompt_by_name
)
from apps.template.models.template_prompt_model import TemplatePromptInfo
from common.core.deps import SessionDep, CurrentUser, Trans
from common.utils.utils import SQLBotLogUtil

router = APIRouter(tags=["Template Prompt"], prefix="/system/template-prompt")


"""分页查询模板提示词"""
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

    current_page, page_size, total_count, total_pages, _list = page_template_prompt(
        session=session,
        current_page=current_page,
        page_size=page_size,
        oid=current_user.oid,
        type=type,
        name=name,
        datasource_id=datasource_id
    )

    data_list = []
    skipped_count = 0
    for item in _list:
        item_dict = {}
        if hasattr(item, '_fields'):
            try:
                from sqlmodel import SQLModel
                for field_item, key in zip(item, item._fields):
                    if isinstance(field_item, SQLModel):
                        item_dict.update(field_item.model_dump())
                    else:
                        item_dict[key] = field_item
            except Exception:
                item_dict = {}
        
        # 跳过无效记录，无法通过验证
        if item_dict.get('type') is None or item_dict.get('content') is None:
            skipped_count += 1
            SQLBotLogUtil.debug(f"Skipped invalid record: id={item_dict.get('id')}, type={item_dict.get('type')}, content={'None' if item_dict.get('content') is None else 'exists'}")
            continue
        
        try:
            data_list.append(TemplatePromptInfo.model_validate(item_dict))

        except Exception as e:
            skipped_count += 1
            SQLBotLogUtil.debug(f"Validation failed for record id={item_dict.get('id')}: {str(e)}")
            continue
    
    if skipped_count > 0:
        SQLBotLogUtil.info(f"Filtered {skipped_count} invalid records out of {len(_list)} total records")

    return {
        "current_page": current_page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "data": data_list
    }

"""创建或更新模板提示词"""
@router.put("")
async def create_or_update(
    session: SessionDep,
    current_user: CurrentUser,
    trans: Trans,
    info: TemplatePromptInfo
):
    oid = current_user.oid
    if info.id:
        result = update_template_prompt(session, info, oid, trans)
    else:
        result = create_template_prompt(session, info, oid, trans)
    
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

"""删除模板提示词"""
@router.delete("")
async def delete(
    session: SessionDep,
    current_user: CurrentUser,
    id_list: list[int]
):
    delete_template_prompt(session, id_list, current_user.oid)


"""启用/禁用模板提示词"""
@router.get("/{id}/enable/{enabled}")
async def enable(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    enabled: bool,
    trans: Trans
):

    result = enable_template_prompt(session, id, enabled, current_user.oid, trans)
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


@router.get("/name/{name}")
async def get_by_name(
    session: SessionDep,
    current_user: CurrentUser,
    name: str
):
    """根据名称获取模板提示词"""
    template_prompt = get_template_prompt_by_name(session, name, current_user.oid)
    if not template_prompt:
        raise HTTPException(status_code=404, detail="Template prompt not found")
    
    # 处理不同的返回类型（SQLModel 对象或 Row 对象）
    if hasattr(template_prompt, 'model_dump'):
        # 如果是 SQLModel 对象，使用 model_dump
        result_dict = template_prompt.model_dump()
    elif hasattr(template_prompt, '_fields'):
        # 如果是 Row 对象，从 _fields 提取
        from sqlmodel import SQLModel
        result_dict = {}
        for field_item, key in zip(template_prompt, template_prompt._fields):
            if isinstance(field_item, SQLModel):
                result_dict.update(field_item.model_dump())
            else:
                result_dict[key] = field_item
    else:
        # 直接访问属性
        result_dict = {
            "id": getattr(template_prompt, 'id', None),
            "oid": getattr(template_prompt, 'oid', None),
            "type": getattr(template_prompt, 'type', None),
            "name": getattr(template_prompt, 'name', None),
            "content": getattr(template_prompt, 'content', None),
            "datasource_id": getattr(template_prompt, 'datasource_id', None),
            "enabled": getattr(template_prompt, 'enabled', None),
            "create_time": getattr(template_prompt, 'create_time', None),
            "update_time": getattr(template_prompt, 'update_time', None)
        }
    
    return TemplatePromptInfo.model_validate(result_dict)

