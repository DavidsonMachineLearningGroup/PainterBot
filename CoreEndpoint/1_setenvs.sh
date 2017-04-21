#!/bin/bash
export SLACK_OAUTH_CLIENT_ID=
export SLACK_OAUTH_CLIENT_SECRET=
export SLACK_SECRETTOKEN=
export VERIFICAITON_TOKEN=
export OAUTHLIB_RELAX_TOKEN_SCOPE=1
export OAUTHLIB_INSECURE_TRANSPORT=1

# python slack.py
# celery worker --concurrency 1 -A gpucelery --loglevel=info
