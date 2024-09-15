# import unittest

# from stellarbot import StellarBot


# class TestTradeAggregations(unittest.TestCase):
#     def setUp(self):
#         self.bot = StellarBot()

#     def test_get_trade_aggregations_no_aggregations(self):
#         # Mock the server response to simulate no trade aggregations found
#         self.bot.server.trade_aggregations = self.mock_trade_aggregations_no_aggregations

#         result = self.bot.get_trade_aggregations()

#         self.assertEqual(result, [])

#     def mock_trade_aggregations_no_aggregations(self, *args, **kwargs):
#         # Mock the trade_aggregations method to return an empty list of trade aggregations
#         return {'_embedded': {'records': []}}


# if __name__ == '__main__':
#     unittest.main()