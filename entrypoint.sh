#!/bin/bash

set -e
#set -o pipefail
source $(pwd)/run.sh
rc=$(run $@ >> $LOG_FILE)
exit $rc