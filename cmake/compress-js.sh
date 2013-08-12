#!/bin/bash

if type closure &> /dev/null; then
    __compressjs() {
        closure --jscomp_off internetExplorerChecks --warning_level QUIET \
            --js_output_file "$2" "$1"
    }
else
    __compressjs() {
        cp "$1" "$2"
    }
fi

__compressjs "$1" "$2"
