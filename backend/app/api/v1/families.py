from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.services.family_service import FamilyService
from app.schemas.family import (
    FamilyCreate, FamilyResponse, FamilyDetail,
    JoinFamily, UpdateMemberRole, FamilyMember
)

router = APIRouter(prefix="/families", tags=["家庭协作"])


@router.post("", response_model=FamilyResponse)
def create_family(
    data: FamilyCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """创建家庭"""
    service = FamilyService(db)
    try:
        return service.create(data.name, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=FamilyDetail)
def get_my_family(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取我的家庭"""
    service = FamilyService(db)
    family = service.get_user_family(current_user.id)
    if not family:
        raise HTTPException(status_code=404, detail="未加入任何家庭")
    members = service.get_members(family.id)
    return FamilyDetail(
        id=family.id,
        name=family.name,
        owner_id=family.owner_id,
        invite_code=family.invite_code,
        created_at=family.created_at,
        members=members
    )


@router.post("/join", response_model=FamilyResponse)
def join_family(
    data: JoinFamily,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """通过邀请码加入家庭"""
    service = FamilyService(db)
    try:
        return service.join_by_code(data.invite_code, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/invite-code", response_model=dict)
def regenerate_invite_code(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """重新生成邀请码"""
    service = FamilyService(db)
    family = service.get_user_family(current_user.id)
    if not family:
        raise HTTPException(status_code=404, detail="未加入任何家庭")
    try:
        code = service.generate_invite_code(family.id, current_user.id)
        return {"invite_code": code}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.get("/members", response_model=List[FamilyMember])
def get_family_members(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """获取家庭成员列表"""
    service = FamilyService(db)
    family = service.get_user_family(current_user.id)
    if not family:
        raise HTTPException(status_code=404, detail="未加入任何家庭")
    return service.get_members(family.id)


@router.put("/members/{member_id}")
def update_member_role(
    member_id: int,
    data: UpdateMemberRole,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """更新成员角色"""
    service = FamilyService(db)
    family = service.get_user_family(current_user.id)
    if not family:
        raise HTTPException(status_code=404, detail="未加入任何家庭")
    try:
        service.update_member_role(family.id, member_id, data.role, current_user.id)
        return {"message": "更新成功"}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/members/{member_id}")
def remove_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """移除家庭成员"""
    service = FamilyService(db)
    family = service.get_user_family(current_user.id)
    if not family:
        raise HTTPException(status_code=404, detail="未加入任何家庭")
    try:
        service.remove_member(family.id, member_id, current_user.id)
        return {"message": "移除成功"}
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=403, detail=str(e))
