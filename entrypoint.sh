#!/bin/bash

echo "{
  \"openai_api_key\": \"${OPENAI_API_KEY:-YOUR API SECRET KEY}\",
  \"openai_api_base\": \"${OPENAI_API_BASE:-https://api.openai.com/v1}\",
  \"model\": \"${MODEL:-gpt-3.5-turbo}\",
  \"use_azure_chatgpt\": ${USE_AZURE_CHATGPT:-false},
  \"azure_deployment_id\": \"${AZURE_DEPLOYMENT_ID:-}\",
  \"role_desc\": \"${ROLE_DESC:-You are a helpful assistant.}\",
  \"session_expired_duration\": ${SESSION_EXPIRED_DURATION:-3600},
  \"max_tokens\": ${MAX_TOKENS:-1000},
  \"temperature\": ${TEMPERATURE:-0.9},
  \"proxy\": \"${PROXY:-}\",
  \"create_image_prefix\": ${CREATE_IMAGE_PREFIX:-[\"画\", \"看\", \"找\"]},
  \"create_image_model\": \"${CREATE_IMAGE_MODEL:-dall-e-3}\",
  \"create_image_size\": \"${CREATE_IMAGE_SIZE:-1024x1024}\",
  \"create_image_style\": \"${CREATE_IMAGE_STYLE:-vivid}\",
  \"create_image_quality\": \"${CREATE_IMAGE_QUALITY:-hd}\",
  \"clear_current_session_command\": \"${CLEAR_CURRENT_SESSION_COMMAND:-#clear session}\",
  \"clear_all_sessions_command\": \"${CLEAR_ALL_SESSIONS_COMMAND:-#clear all sessions}\",
  \"chat_group_session_independent\": ${CHAT_GROUP_SESSION_INDEPENDENT:-false},
  \"single_chat_prefix\": ${SINGLE_CHAT_PREFIX:-[\"bot\", \"@bot\"]},
  \"query_key_command\": \"${QUERY_KEY_COMMAND:-#query key}\",
  \"recent_days\": ${RECENT_DAYS:-5},
  \"plugins\": ${PLUGINS:-[{ \"name\": \"tiktok\", \"command\": \"#tiktok\" }]},
  \"openai_sensitive_id\": \"${OPENAI_SENSITIVE_ID:-}\",
  \"server_host\": \"${SERVER_HOST:-127.0.0.1:5555}\"
}" > config.json

# 启动应用
python app.py
