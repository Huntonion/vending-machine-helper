LOG_GROUP_NAME="/aws/lambda/sale"

LOG_STREAM_NAME=$(aws --endpoint-url=http://localhost:4566 logs 
describe-log-streams --log-group-name "${LOG_GROUP_NAME}" | jq -r 
'.logStreams | sort_by(.creationTime) | .[-1].logStreamName')

aws --endpoint-url=http://localhost:4566 logs get-log-events 
--log-group-name "${LOG_GROUP_NAME}" --log-stream-name 
"${LOG_STREAM_NAME}" | jq -r '.events[] | select(has("message")) | 
.message'
