import time
from utils.jwt import sign_jwt, decode_jwt
import jwt
credentials= {"msisdn": '1234567891'}

token = sign_jwt(credentials, 5)
time.sleep(10)
try:
  decode = decode_jwt('hhffhfh@')
  print(decode)
  # print(decode["data"],decode["expires"])
except jwt.exceptions.DecodeError as ex:
  print('it is intercepted')
#print(decoded_token["expires"])
