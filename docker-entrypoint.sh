#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Trace execution
[[ "${DEBUG}" ]] && set -x


###
# Setup cloud private key.
###
function setup_cloud_key() {
  echo "${INPUT_CLOUDKEY}" | base64 -d > cloud_private_key
  chmod 400 cloud_private_key
}

####
# Clone private deployment repository (Arkhn's ansible playbooks).
####
function clone_deployment() {
  deployment_dir="$1"

  echo "${INPUT_DEPLOYMENTTOKEN}" | base64 -d > deployment_deploy_key
  chmod 400 deployment_deploy_key
  ssh-keyscan -H github.com >> known_hosts
  GIT_SSH_COMMAND="ssh -o IdentityFile=deployment_deploy_key -o IdentitiesOnly=yes -o UserKnownHostsFile=known_hosts" git clone git@github.com:arkhn/deployment.git "${deployment_dir}"

  pushd deployment/stack
  ansible-galaxy role install -r requirements.yml
  ansible-galaxy collection install -r requirements.yml
  popd
}

setup_cloud_key

deployment_dir=./deployment

if [[ ! -d "${deployment_dir}" ]]; then
  clone_deployment "${deployment_dir}"
fi

# Build arguments array for testy-action
declare -a flags
flags=("${INPUT_CLOUDTOKEN}" "${INPUT_CLOUDPROJECTID}" cloud_private_key)
flags+=(--playbook-dir deployment/stack)

if [[ ! -z "${INPUT_CONTEXTNAME}" ]]; then
  flags+=(--context-name ${INPUT_CONTEXTNAME})
fi

if [[ "${DEBUG}" ]]; then
  flags+=(--debug)
fi

testy-action "${flags[@]}"
