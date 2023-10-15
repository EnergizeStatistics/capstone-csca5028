#! /bin/bash

if [ -z "$PORT" ] ; then
	echo "Fatal: missing mandatory environment variable PORT." 1>&2
	exit -1
fi

echo 'getting docker' 1>&2
./release/docker.sh
if [ "$?" -ne 0 ]; then
	echo "Fatal error getting docker" 1>&2
	exit -1
fi

echo 'getting python' 1>&2
./release/python.sh
if [ "$?" -ne 0 ]; then
	echo "Fatal error getting python" 1>&2
	exit -1
fi

echo 'getting rabbitmq' 1>&2
./release/rabbitmq.sh
if [ "$?" -ne 0 ]; then
	echo "Fatal error getting python" 1>&2
	exit -1
fi

echo 'getting remaining apt dependencies' 1>&2
./release/apt-get.sh
if [ "$?" -ne 0 ]; then
	echo "Fatal error getting remaining apt dependencies" 1>&2
	exit -1
fi

echo 'getting remaining pip dependencies' 1>&2
pip install -r ./requirements.txt
if [ "$?" -ne 0 ]; then
	echo "Fatal error getting remaining pip dependencies" 1>&2
	exit -1
fi
exit 0
