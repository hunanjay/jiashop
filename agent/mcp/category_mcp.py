from db.models import ProductCategory

def get_all_categories():
    """获取所有激活的礼品分类"""
    categories = ProductCategory.query.filter_by(active=True).all()
    if not categories:
        return "暂无分类。"
    names = [c.name for c in categories]
    return f"咱们店内目前支持：{ '、'.join(names) }。您想了解哪个分类？"
