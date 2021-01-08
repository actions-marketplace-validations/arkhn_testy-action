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
  deployment_ref="$3"

  known_hosts_file="$2"
  deploy_key=./deployment_deploy_key

  if [[ -d "${deployment_dir}" ]]; then
    return
  fi;

  ssh-keyscan -H github.com >> "${known_hosts_file}"

  echo "${INPUT_DEPLOYMENTTOKEN}" | base64 -d > "${deploy_key}"
  chmod 400 "${deploy_key}"
  GIT_SSH_COMMAND="ssh -o IdentityFile=${deploy_key} -o IdentitiesOnly=yes -o UserKnownHostsFile=${known_hosts_file}" git clone git@github.com:arkhn/deployment.git "${deployment_dir}"

  pushd "${deployment_dir}"
  git checkout "${deployment_ref}"
  popd

  pushd "${deployment_dir}/stack"
  ansible-galaxy role install -r requirements.yml
  ansible-galaxy collection install -r requirements.yml
  popd
}

known_hosts_file=./known_hosts
deployment_dir=./deployment
deployment_ref="${INPUT_DEPLOYMENTREF}"

clone_deployment "${deployment_dir}" "${known_hosts_file}" "${deployment_ref}"
setup_cloud_key

# Build arguments array for testy-action
declare -a flags
flags=("${INPUT_CLOUDTOKEN}" "${INPUT_CLOUDPROJECTID}" cloud_private_key)
flags+=(--playbook-dir deployment/stack)

if [[ ! -z "${INPUT_CONTEXTNAME}" ]]; then
  flags+=(--context-name ${INPUT_CONTEXTNAME})
fi

if [[ ! -z "${INPUT_VERSIONS}" ]]; then
  flags+=(--versions "${INPUT_VERSIONS}")
fi

if [[ "${DEBUG}" ]]; then
  flags+=(--debug)
fi

if [[ ! -z "${INPUT_VERBOSE}" ]]; then
  flags+=(--verbose)
fi

testy-action "${flags[@]}"
