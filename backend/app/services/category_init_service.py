from sqlalchemy.orm import Session
from app.models import Category


class CategoryInitService:
    """预设分类初始化服务"""

    # 支出分类 - 父分类
    EXPENSE_PARENT_CATEGORIES = [
        {"name": "孩子支出", "icon": "👶", "type": "expense"},
        {"name": "家庭固定支出", "icon": "🏠", "type": "expense"},
        {"name": "家庭不固定支出", "icon": "🛒", "type": "expense"},
        {"name": "家庭旅行支出", "icon": "✈️", "type": "expense"},
        {"name": "成长支出", "icon": "📚", "type": "expense"},
        {"name": "其他支出", "icon": "📝", "type": "expense"},
    ]

    # 支出分类 - 子分类
    EXPENSE_CHILD_CATEGORIES = {
        "孩子支出": [
            {"name": "学费", "icon": "📚"},
            {"name": "课外班", "icon": "🎨"},
            {"name": "玩具娱乐", "icon": "🎮"},
            {"name": "童装", "icon": "👔"},
            {"name": "医疗", "icon": "💊"},
            {"name": "零食", "icon": "🍪"},
        ],
        "家庭固定支出": [
            {"name": "人寿保险", "icon": "🛡️"},
            {"name": "车险", "icon": "🚗"},
            {"name": "生活缴费", "icon": "💡"},
            {"name": "房租/房贷", "icon": "🏠"},
            {"name": "通讯费", "icon": "📱"},
            {"name": "订阅服务", "icon": "📺"},
        ],
        "家庭不固定支出": [
            {"name": "餐饮", "icon": "🍜"},
            {"name": "超市购物", "icon": "🛒"},
            {"name": "服装鞋包", "icon": "👗"},
            {"name": "交通出行", "icon": "🚕"},
            {"name": "美容护肤", "icon": "💄"},
            {"name": "数码电子", "icon": "📱"},
            {"name": "烟酒茶", "icon": "🍺"},
        ],
        "家庭旅行支出": [
            {"name": "机票火车票", "icon": "🎫"},
            {"name": "酒店住宿", "icon": "🏨"},
            {"name": "景点门票", "icon": "🎢"},
            {"name": "旅行购物", "icon": "🛍️"},
        ],
        "成长支出": [
            {"name": "健身运动", "icon": "💪"},
            {"name": "书籍阅读", "icon": "📖"},
            {"name": "学习培训", "icon": "🎓"},
            {"name": "心理咨询", "icon": "🧠"},
        ],
        "其他支出": [
            {"name": "人情往来", "icon": "🎁"},
            {"name": "医疗健康", "icon": "🏥"},
            {"name": "宠物", "icon": "🐶"},
            {"name": "其他", "icon": "📝"},
        ],
    }

    # 收入分类 - 父分类
    INCOME_PARENT_CATEGORIES = [
        {"name": "工资收入", "icon": "💵", "type": "income"},
        {"name": "其他收入", "icon": "💼", "type": "income"},
    ]

    # 收入分类 - 子分类
    INCOME_CHILD_CATEGORIES = {
        "工资收入": [
            {"name": "月薪", "icon": "💵"},
            {"name": "年终奖", "icon": "🎁"},
            {"name": "加班费", "icon": "⏰"},
            {"name": "福利补贴", "icon": "🎀"},
        ],
        "其他收入": [
            {"name": "兼职外快", "icon": "💼"},
            {"name": "投资收益", "icon": "📈"},
            {"name": "利息收入", "icon": "🏦"},
            {"name": "退款", "icon": "🔙"},
            {"name": "礼金", "icon": "💌"},
            {"name": "其他", "icon": "📝"},
        ],
    }

    # 投资分类（无父子层级）
    INVESTMENT_CATEGORIES = [
        {"name": "股票", "icon": "📈", "type": "investment"},
        {"name": "基金", "icon": "📊", "type": "investment"},
        {"name": "银行理财", "icon": "🏦", "type": "investment"},
        {"name": "定期存款", "icon": "📅", "type": "investment"},
        {"name": "债券", "icon": "📄", "type": "investment"},
        {"name": "公积金", "icon": "🏠", "type": "investment"},
        {"name": "养老保险", "icon": "🛡️", "type": "investment"},
    ]

    @classmethod
    def init_categories_for_user(cls, db: Session, user_id: int) -> None:
        """为用户初始化预设分类"""
        # 检查是否已有分类
        existing = db.query(Category).filter(Category.user_id == user_id).first()
        if existing:
            return  # 已有分类，不再初始化

        # 存储已创建的父分类ID映射
        parent_id_map = {}
        sort_order = 0

        # 1. 创建支出父分类
        for cat_data in cls.EXPENSE_PARENT_CATEGORIES:
            category = Category(
                user_id=user_id,
                name=cat_data["name"],
                icon=cat_data["icon"],
                type=cat_data["type"],
                parent_id=None,
                sort_order=sort_order
            )
            db.add(category)
            db.flush()  # 获取ID
            parent_id_map[cat_data["name"]] = category.id
            sort_order += 1

        # 2. 创建支出子分类
        for parent_name, children in cls.EXPENSE_CHILD_CATEGORIES.items():
            parent_id = parent_id_map.get(parent_name)
            for child_data in children:
                category = Category(
                    user_id=user_id,
                    name=child_data["name"],
                    icon=child_data["icon"],
                    type="expense",
                    parent_id=parent_id,
                    sort_order=sort_order
                )
                db.add(category)
                sort_order += 1

        # 3. 创建收入父分类
        for cat_data in cls.INCOME_PARENT_CATEGORIES:
            category = Category(
                user_id=user_id,
                name=cat_data["name"],
                icon=cat_data["icon"],
                type=cat_data["type"],
                parent_id=None,
                sort_order=sort_order
            )
            db.add(category)
            db.flush()
            parent_id_map[cat_data["name"]] = category.id
            sort_order += 1

        # 4. 创建收入子分类
        for parent_name, children in cls.INCOME_CHILD_CATEGORIES.items():
            parent_id = parent_id_map.get(parent_name)
            for child_data in children:
                category = Category(
                    user_id=user_id,
                    name=child_data["name"],
                    icon=child_data["icon"],
                    type="income",
                    parent_id=parent_id,
                    sort_order=sort_order
                )
                db.add(category)
                sort_order += 1

        # 5. 创建投资分类（无父子层级）
        for cat_data in cls.INVESTMENT_CATEGORIES:
            category = Category(
                user_id=user_id,
                name=cat_data["name"],
                icon=cat_data["icon"],
                type=cat_data["type"],
                parent_id=None,
                sort_order=sort_order
            )
            db.add(category)
            sort_order += 1

        db.commit()

    @classmethod
    def reset_categories_for_user(cls, db: Session, user_id: int) -> None:
        """重置用户分类（删除自定义，保留预设）"""
        # 删除用户的所有分类
        db.query(Category).filter(Category.user_id == user_id).delete()
        db.commit()
        # 重新初始化
        cls.init_categories_for_user(db, user_id)

    @classmethod
    def rebuild_parent_child_structure(cls, db: Session) -> None:
        """重建父子分类结构（用于现有数据迁移）"""
        # 获取所有用户ID
        user_ids = db.query(Category.user_id).distinct().filter(Category.user_id.isnot(None)).all()
        for (user_id,) in user_ids:
            # 删除现有分类
            db.query(Category).filter(Category.user_id == user_id).delete()
            db.commit()
            # 重新初始化
            cls.init_categories_for_user(db, user_id)
