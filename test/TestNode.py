import random
import unittest

import node as NodeClass

peertype = ['buyer', 'seller']
BUYER = 'buyer'
SELLER = 'seller'

products = ['fish', 'salt', 'boars']


class TestNode(unittest.TestCase):

    def test_transact(self):  # Tests logic of transact function
        seller_node = NodeClass.Node()
        buyer_node = NodeClass.Node()
        seller_node.init('P1', 'DummyIP1', SELLER, product_count=random.randint(-10, 10))
        buyer_node.init('P2', 'DummyIP2', BUYER, product_count=random.randint(-10, 10))
        buyer_node.product_to_buy = random.choice(products)
        initial_product_count = seller_node.product_count
        seller_node.transact('P2')
        final_product_count = seller_node.product_count
        if seller_node.peertype == SELLER:
            if initial_product_count < 1:
                assert final_product_count == 3
            else:
                if buyer_node.product_to_buy != seller_node.product_name:
                    assert final_product_count == initial_product_count
                else:
                    assert final_product_count == initial_product_count - 1


if __name__ == '__main__':
    unittest.main()
