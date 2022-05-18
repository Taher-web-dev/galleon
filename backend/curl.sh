#!/bin/sh -x 

curl -s -H 'content-type: application/json' -d '{"name":"kefah", "msisdn":"5070704747", "password":"BiggerHello", "otp_confirmation":"123"}' 127.0.0.1:8080/api/user/create | jq
curl -s -H 'content-type: application/json' -d '{"msisdn":"5070704747", "password":"BiggerHello"}' 127.0.0.1:8080/api/user/login | jq
TOKEN=$(curl -s -H 'content-type: application/json' -d '{"msisdn":"5070704747", "password":"BiggerHello"}' 127.0.0.1:8080/api/user/login | jq -r .data.access_token)
curl -s -H 'content-type: application/json' -H "Authorization: Bearer $TOKEN" -X PATCH -d '{"email":"kefah@startappz.com"}' 127.0.0.1:8080/api/user/profile | jq
curl -s -H 'content-type: application/json' -H "Authorization: Bearer $TOKEN" 127.0.0.1:8080/api/user/profile | jq
curl -s -H 'content-type: application/json' -H "Authorization: Bearer $TOKEN" -d '{}' 127.0.0.1:8080/api/user/delete | jq

