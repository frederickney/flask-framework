#!/bin/bash

set -e
#set -o pipefail
source /srv/http/run.sh
rc=$(run $@)
exit $rc