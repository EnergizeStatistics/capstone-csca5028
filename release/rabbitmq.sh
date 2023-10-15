#! /bin/bash
NAME="CARBON_RABBIT"

docker pull --quiet rabbitmq:3

ID="$(docker container ls --quiet --all --filter name="$NAME")"
if [[ -z "$ID" ]] ; then
	docker create --quiet -p 5672:5672 --name "$NAME" rabbitmq:3
	ID="$(docker container ls --quiet --all --filter name="$NAME")"
fi

if [[ -z "$ID" ]] ; then
	echo "Unable to create container" 1>&2
	exit 1
fi

docker start "$ID"
