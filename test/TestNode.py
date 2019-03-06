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

    def test_concurrency(self):
        seller_node = NodeClass.Node()
        buyer_node1 = NodeClass.Node()
        buyer_node2 = NodeClass.Node()

        seller_node.init('P1', 'DummyIP1', SELLER, product_count=random.randint(1, 10))
        initial_product_count = seller_node.product_count
        buyer_node1.init('P2', 'DummyIP2', BUYER)
        buyer_node1.product_to_buy = 'salt'
        buyer_node2.init('P3', 'DummyIP3', BUYER)
        buyer_node2.product_to_buy = 'salt'
        buyer_node1.transact(buyer_node1.node_id)
        buyer_node2.transact(buyer_node1.node_id)
        final_product_count = seller_node.product_count
        assert final_product_count == initial_product_count - 2


if __name__ == '__main__':
    unittest.main()
