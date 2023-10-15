#! /bin/bash

if [ -z "$PORT" ] ; then
	echo "Fatal: missing mandatory environment variable PORT." 1>&2
	exit -1
fi

exit 0
