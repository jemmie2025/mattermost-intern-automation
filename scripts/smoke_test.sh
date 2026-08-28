#!/usr/bin/env bash
set -euo pipefail

bot_url="${BOT_URL:-http://127.0.0.1:8080}"
checkin_token="${MM_CHECKIN_TOKEN:-change-me-checkin}"
checkout_token="${MM_CHECKOUT_TOKEN:-change-me-checkout}"
task_token="${MM_TASK_TOKEN:-change-me-task}"
faq_token="${MM_FAQ_TOKEN:-change-me-faq}"
webhook_token="${MM_OUTGOING_WEBHOOK_TOKEN:-change-me-webhook}"
demo_user="smoke-$(date +%s)"

curl --fail --silent --show-error "${bot_url}/health/ready"

curl --fail --silent --show-error --request POST \
  --data-urlencode "token=${checkin_token}" \
  --data-urlencode "user_id=${demo_user}" \
  --data-urlencode "user_name=smoke_test" \
  --data-urlencode "channel_id=local-test" \
  --data-urlencode "text=Automated smoke test" \
  "${bot_url}/mattermost/commands/checkin"

curl --fail --silent --show-error --request POST \
  --data-urlencode "token=${task_token}" \
  --data-urlencode "user_id=${demo_user}" \
  --data-urlencode "user_name=smoke_test" \
  --data-urlencode "channel_id=local-test" \
  --data-urlencode "text=Executed smoke test | None | Review results" \
  "${bot_url}/mattermost/commands/task"

curl --fail --silent --show-error --request POST \
  --data-urlencode "token=${faq_token}" \
  --data-urlencode "user_id=${demo_user}" \
  --data-urlencode "user_name=smoke_test" \
  --data-urlencode "channel_id=local-test" \
  --data-urlencode "text=vpn" \
  "${bot_url}/mattermost/commands/faq"

curl --fail --silent --show-error --request POST \
  --header "Content-Type: application/json" \
  --data "{\"token\":\"${webhook_token}\",\"text\":\"vpn setup\",\"trigger_word\":\"vpn\",\"user_id\":\"${demo_user}\"}" \
  "${bot_url}/mattermost/webhooks/faq-keyword"

curl --fail --silent --show-error --request POST \
  --data-urlencode "token=${checkout_token}" \
  --data-urlencode "user_id=${demo_user}" \
  --data-urlencode "user_name=smoke_test" \
  --data-urlencode "channel_id=local-test" \
  --data-urlencode "text=Smoke test completed" \
  "${bot_url}/mattermost/commands/checkout"

printf '\nSmoke test completed successfully.\n'

