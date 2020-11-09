#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Trace execution
[[ "${DEBUG}" ]] && set -x


####
# Clone private deployment repository (Arkhn's ansible playbooks).
####
function clone_deployment() {
  echo "${INPUT_DEPLOYMENTTOKEN}" | base64 -d > deployment_deploy_key
  chmod 400 deployment_deploy_key
  ssh-keyscan github.com >> known_hosts
  GIT_SSH_COMMAND="ssh -o IdentityFile=deployment_deploy_key -o IdentitiesOnly=yes -o UserKnownHostsFile=known_hosts" git clone git@github.com:arkhn/deployment.git
}

clone_deployment

# Build arguments array for testy-action
declare -a flags
flags=("${INPUT_CLOUDTOKEN}" "${INPUT_CLOUDPROJECTID}")

if [[ ! -z "${INPUT_CONTEXTNAME}" ]]; then
  flags+=(--context-name $INPUT_CONTEXTNAME)
fi

testy-action "${flags[@]}"
