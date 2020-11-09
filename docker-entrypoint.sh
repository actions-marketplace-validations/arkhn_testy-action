#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Trace execution
[[ "${DEBUG}" ]] && set -x

function clone_deployment() {
  mkdir -p ~/.ssh/deployment
  echo "${INPUT_DEPLOYMENTTOKEN}" > ~/.ssh/deployment/deploy_key
  chmod 400 ~/.ssh/deployment/deploy_key
  cat > ~/.ssh/deployment/config <<-EOF
  Host github.com
    Hostname github.com
    IdentityFile ~/.ssh/deployment/deploy_key
    IdentitiesOnly yes
    UserKnownHostsFile ~/.ssh/deployment/known_hosts
EOF
  ssh-keyscan github.com > ~/.ssh/deployment/known_hosts
  GIT_SSH_COMMAND="ssh -F ~/.ssh/deployment/config" git clone git@github.com:arkhn/deployment.git
}

clone_deployment

testy-action "${INPUT_CONTEXTNAME:+--context-name $INPUT_CONTEXTNAME}" "${INPUT_CLOUDTOKEN}" "${INPUT_CLOUDPROJECTID}"