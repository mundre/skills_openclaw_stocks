#!/bin/bash
# Search flight tickets via ibotservice API
# Usage: searchFlights.sh <depCountry> <arrCountry> <isBusiness> <depCity> <arrCity> <currency> <depDate> <subQuery>

set -e

# Parameters
DEP_COUNTRY="$1"
ARR_COUNTRY="$2"
IS_BUSINESS="$3"
DEP_CITY="$4"
ARR_CITY="$5"
CURRENCY="$6"
DEP_DATE="$7"
SUB_QUERY="$8"

# Build JSON payload
JSON_PAYLOAD=$(cat <<EOF
{
  "token": "003d2b7d-1ef9-4827-ab9b-cae765689f9d",
  "botId": "2026030610103389649",
  "bizUserId": "2107220265020227",
  "chatContent": {
    "contentType": "TEXT",
    "text": "{\"depCountry\":\"${DEP_COUNTRY}\",\"arrCountry\":\"${ARR_COUNTRY}\",\"isBusiness\":${IS_BUSINESS},\"arrCity\":\"${ARR_CITY}\",\"depCity\":\"${DEP_CITY}\",\"currency\":\"${CURRENCY}\",\"depDate\":\"${DEP_DATE}\",\"subQuery\":\"${SUB_QUERY}\"}"
  },
  "botVariables": {
    "userId": "2107220265020227",
    "serviceType": "RECALL_flight"
  },
  "stream": false
}
EOF
)

# Make API call
curl --silent --location 'https://ibotservice.alipayplus.com/almpapi/v1/message/chat' \
  --header 'Content-Type: application/json' \
  --data "$JSON_PAYLOAD"
