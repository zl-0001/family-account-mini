from sqlalchemy.orm import Session
from app.models import Family, User
from typing import Optional, List
import secrets


class FamilyService:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, user_id: int) -> Family:
        """创建家庭"""
        # 检查用户是否已在家庭中
        user = self.db.query(User).filter(User.id == user_id).first()
        if user.family_id:
            raise ValueError("用户已在家庭中")

        # 生成邀请码
        invite_code = secrets.token_hex(4).upper()

        family = Family(
            name=name,
            owner_id=user_id,
            invite_code=invite_code
        )
        self.db.add(family)
        self.db.flush()

        # 更新用户的家庭ID和角色
        user.family_id = family.id
        user.role = "owner"
        self.db.commit()
        self.db.refresh(family)
        return family

    def get_by_id(self, family_id: int) -> Optional[Family]:
        """获取家庭详情"""
        return self.db.query(Family).filter(Family.id == family_id).first()

    def get_user_family(self, user_id: int) -> Optional[Family]:
        """获取用户所属家庭"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user or not user.family_id:
            return None
        return self.get_by_id(user.family_id)

    def generate_invite_code(self, family_id: int, user_id: int) -> str:
        """生成新的邀请码"""
        family = self.get_by_id(family_id)
        if not family:
            raise ValueError("家庭不存在")
        if family.owner_id != user_id:
            raise PermissionError("仅家庭创建者可生成邀请码")

        family.invite_code = secrets.token_hex(4).upper()
        self.db.commit()
        return family.invite_code

    def join_by_code(self, invite_code: str, user_id: int) -> Family:
        """通过邀请码加入家庭"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if user.family_id:
            raise ValueError("用户已在家庭中")

        family = self.db.query(Family).filter(Family.invite_code == invite_code).first()
        if not family:
            raise ValueError("邀请码无效")

        user.family_id = family.id
        user.role = "member"
        self.db.commit()
        self.db.refresh(family)
        return family

    def get_members(self, family_id: int) -> List[dict]:
        """获取家庭成员列表"""
        members = self.db.query(User).filter(User.family_id == family_id).all()
        result = []
        for m in members:
            result.append({
                "user_id": m.id,
                "username": m.username,
                "nickname": m.nickname,
                "avatar": m.avatar,
                "role": m.role,
                "joined_at": m.updated_at
            })
        return result

    def update_member_role(self, family_id: int, member_id: int, role: str, requester_id: int) -> bool:
        """更新成员角色"""
        family = self.get_by_id(family_id)
        if not family:
            raise ValueError("家庭不存在")

        # 只有 owner 可以修改角色
        if family.owner_id != requester_id:
            raise PermissionError("仅家庭创建者可修改成员角色")

        # 不能修改 owner 角色
        if member_id == family.owner_id:
            raise ValueError("不能修改创建者角色")

        member = self.db.query(User).filter(User.id == member_id, User.family_id == family_id).first()
        if not member:
            raise ValueError("成员不存在")

        member.role = role
        self.db.commit()
        return True

    def remove_member(self, family_id: int, member_id: int, requester_id: int) -> bool:
        """移除家庭成员"""
        family = self.get_by_id(family_id)
        if not family:
            raise ValueError("家庭不存在")

        if family.owner_id != requester_id and requester_id != member_id:
            raise PermissionError("无权移除此成员")

        if member_id == family.owner_id:
            raise ValueError("不能移除创建者")

        member = self.db.query(User).filter(User.id == member_id, User.family_id == family_id).first()
        if not member:
            raise ValueError("成员不存在")

        member.family_id = None
        member.role = "member"
        self.db.commit()
        return True
