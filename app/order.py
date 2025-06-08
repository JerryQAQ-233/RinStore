from flask import jsonify, url_for
import uuid

from .data_manager import get_unpaid_orders, save_unpaid_orders
from .data_manager import add_recharge_history

class OrderCreator:
    def __init__(self, data):
        self.data = data
        self.order_type = data.get('type')
        self.confirmation_id = str(uuid.uuid4())
        self.order_id = str(uuid.uuid4())
        self.unpaid_orders = get_unpaid_orders()

    def create_base_order(self, amount, order_type, plan_id=0):
        """创建基础订单并保存"""
        order_info = {
            'order_id': self.order_id,
            'confirmation_id': self.confirmation_id,
            'plan_id': plan_id,
            'amount': amount,
            'status': 'unpaid',
            'type': order_type
        }
        self.unpaid_orders.append(order_info)
        save_unpaid_orders(self.unpaid_orders)
        return order_info

    def get_redirect_response(self, message=None):
        """生成重定向响应"""
        response = {
            'success': True,
            'redirect_url': url_for('payment.payment',
                                  order_id=self.order_id,
                                  confirmation_id=self.confirmation_id,
                                  _external=True)
        }
        if message:
            response['message'] = message
        return jsonify(response)

    def check_existing_order(self):
        """检查订单是否已存在"""
        existing_order = next((order for order in self.unpaid_orders 
                             if order['confirmation_id'] == self.confirmation_id), None)
        if existing_order:
            return jsonify({
                'success': True,
                'redirect_url': url_for('payment.payment',
                                      order_id=existing_order['order_id'],
                                      confirmation_id=existing_order['confirmation_id'],
                                      _external=True)
            })
        return None

    def create_product_order(self):
        """创建产品订单"""
        plan_id = self.data.get('plan_id')
        amount = 10.00 if plan_id == 1 else 20.00
        self.create_base_order(amount, 'product', plan_id)
        print(f"Unpaid product order created: {self.order_id} with confirmation ID {self.confirmation_id}")
        return self.get_redirect_response()

    def create_recharge_order(self):
        """创建充值订单"""
        amount = self.data.get('amount')
        if amount and amount > 0:
            self.create_base_order(amount, 'recharge')
            add_recharge_history(self.order_id, amount, 'unpaid')
            print(f"Unpaid recharge order created: {self.order_id} with confirmation ID {self.confirmation_id}")
            return self.get_redirect_response('Recharge successful!')
        return jsonify({'success': False, 'message': 'Invalid amount.'}), 400

    def process(self):
        """处理订单创建请求"""
        existing_response = self.check_existing_order()
        if existing_response:
            return existing_response

        if self.order_type == 'product':
            return self.create_product_order()
        elif self.order_type == 'recharge':
            return self.create_recharge_order()
        return jsonify({'success': False, 'message': 'Invalid order type.'}), 400

if __name__ == '__main__':
    OrderCreator()