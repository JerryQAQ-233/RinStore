from flask import jsonify, url_for
import uuid
from flask_login import current_user

from .data_manager import global_app as config_app

class OrderCreator:
    def __init__(self, data):
        self.data = data
        self.order_type = data.get('type')
        self.confirmation_id = str(uuid.uuid4())
        self.order_id = str(uuid.uuid4())
        self.unpaid_orders = config_app.get_unpaid_orders()

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
        config_app.save_unpaid_orders(self.unpaid_orders)
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
        product_prices = config_app.get_product_prices()
        amount = product_prices.get(plan_id)
        if amount is None:
            return jsonify({'success': False, 'message': 'Invalid plan ID.'}), 400
        self.create_base_order(amount, 'product', plan_id)
        print(f"Unpaid product order created: {self.order_id} with confirmation ID {self.confirmation_id}")
        return self.get_redirect_response()

    def create_recharge_order(self):
        """创建充值订单"""
        amount = self.data.get('amount')
        if amount and amount > 0:
            self.create_base_order(amount, 'recharge')
            config_app.add_recharge_history(current_user.id, self.order_id, amount)
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
    # This block is for testing purposes. In a real application, data would come from a request.
    dummy_data = {
        'type': 'product',
        'plan_id': 1
    }
    creator = OrderCreator(dummy_data)
    # You might want to call creator.process() here to test the flow
    print("OrderCreator initialized with dummy data.")