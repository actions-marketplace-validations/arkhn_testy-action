#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Trace execution
[[ "${DEBUG}" ]] && set -x


####
# Clone private deployment repository (Arkhn's ansible playbooks).
####
function clone_deployment() {
  # Dedicated ssh config for a GitHub deploy key.
  mkdir -p ~/.ssh/deployment
  echo "${INPUT_DEPLOYMENTTOKEN}" | base64 -d > ~/.ssh/deployment/deploy_key
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

# Build arguments array for testy-action
declare -a flags
flags=("${INPUT_CLOUDTOKEN}" "${INPUT_CLOUDPROJECTID}")

if [[ ! -z "${INPUT_CONTEXTNAME}" ]]; then
  flags+=(--context-name $INPUT_CONTEXTNAME)
fi

testy-action "${flags[@]}"
