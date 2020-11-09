#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Trace execution
[[ "${DEBUG}" ]] && set -x

mkdir ~/.ssh
echo "${INPUT_DEPLOYMENTTOKEN}" > ~/.ssh/deploy_key
cat > ~/.ssh/config << EOF
Host github
    Hostname github.com
    IdentityFile ~/.ssh/deploy_key
    IdentitiesOnly yes
EOF

testy-action "${INPUT_CONTEXTNAME:+--context-name $INPUT_CONTEXTNAME}" "${INPUT_CLOUDTOKEN}" "${INPUT_CLOUDPROJECTID}"