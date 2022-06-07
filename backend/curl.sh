#!/bin/sh

MSISDN="5070704747"
PASSWORD="HelloWorld2022"
NAME="Kefah Issa"
EMAIL="kefah@startappz.com"
API_URL=http://127.0.0.1:8080/api

CT="content-type: application/json"

echo "Delete old data"
psql -h 127.0.0.1 -U galleon galleon -c 'delete from users; delete from otp;'

echo "Request OTP"
time curl -s -H "$CT" -d "{\"msisdn\":\"${MSISDN}\"}" ${API_URL}/otp/request | jq
OTP=$(psql -q --csv -t -h 127.0.0.1 -U galleon galleon -c "select code from otp where msisdn='${MSISDN}'; ")

echo "OTP is $OTP"
CONF=$(curl -s -H "$CT" -d "{\"msisdn\":\"${MSISDN}\", \"code\": $OTP}" ${API_URL}/otp/confirm | jq .data.confirmation | tr -d '"')
echo "Confirmation $CONF"

echo "Creating user"
curl -s -H "$CT" -d "{\"name\":\"${NAME}\", \"msisdn\":\"${MSISDN}\", \"password\":\"${PASSWORD}\", \"otp_confirmation\":\"${CONF}\"}" $API_URL/user/create | jq

echo "Login"
curl -s -H "$CT" -d "{\"msisdn\":\"${MSISDN}\", \"password\":\"${PASSWORD}\"}" $API_URL/user/login | jq
TOKEN=$(curl -s -H "$CT" -d "{\"msisdn\":\"${MSISDN}\", \"password\":\"${PASSWORD}\"}" $API_URL/user/login | jq -r .data.access_token)
echo "JWT Token $TOKEN"

echo "Update profile"
curl -s -H "$CT" -H "Authorization: Bearer $TOKEN" -X PATCH -d "{\"email\":\"${EMAIL}\"}" $API_URL/user/profile | jq

echo "Get profile"
curl -s -H "$CT" -H "Authorization: Bearer $TOKEN" $API_URL/user/profile | jq

echo "Delete"
curl -s -H "$CT" -X DELETE -H "Authorization: Bearer $TOKEN" -d '{}' $API_URL/user/delete | jq

