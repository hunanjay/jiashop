from db.models import Order

def get_order_status_logic(order_id: str):
    """底层订单查询逻辑"""
    order = Order.query.get(order_id)
    if not order:
        return f"找不到订单号 {order_id}。"
        
    return {
        "id": order.id,
        "status": order.status,
        "total": order.total_price,
        "created_at": order.created_at.strftime("%Y-%m-%d %H:%M")
    }

def format_order_for_ai(order_info):
    """格式化为 AI 友好的文本"""
    if isinstance(order_info, str):
        return order_info
    return (f"订单单号：{order_info['id']}\n"
            f"订单状态：{order_info['status']}\n"
            f"支付金额：¥{order_info['total']}\n"
            f"下单时间：{order_info['created_at']}")
