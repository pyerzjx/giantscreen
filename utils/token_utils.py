#! usr/bin/python3
# -*- coding: utf-8 -*-
import hmac
# from utils.dbutils import redis
import json


class TokenMaker:

    def generate_token(self, key, message):
        return hmac.new(str(key).encode('utf-8'), str(message).encode('utf-8'), digestmod='MD5').hexdigest()


# class ResolveCacheToken:
#
#     @staticmethod
#     def resolve(token):
#         try:
#             token_seq = redis.get('userID:%s' % token)[5:]
#             # token_seq = redis.get('userID:%s' % token)
#             token = json.loads(token_seq, encoding="utf-8")
#         except Exception as e:
#             return None
#         else:
#             return token


if __name__ == "__main__":
    pass
