#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <deployment_id> [<prefix|bgpu>]"
  exit 1
fi

DEPLID=$1
PREFIX=${2:-bgpu}
echo "Deployment ID: $DEPLID"

set -x
kubectl get services | grep $DEPLID
kubectl expose service ${PREFIX}-lb-$DEPLID --type LoadBalancer --name ${PREFIX}-lb-external-$DEPLID

set +x
while true ; do
  ip=$(kubectl get svc ${PREFIX}-lb-external-$DEPLID -o json | jq -r '.status.loadBalancer.ingress[0].ip ')
  if [[ "$ip" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
    break
  fi
  echo "ip empty, retrying ..."
  sleep 2
done

echo ip=$ip

set -x
az network dns record-set a add-record -g speechservicesdevelopmentwestus2 -z develop2.cris.ai --subscription 3a96ef56-41a9-40a0-b0f3-fb125c2b8798 -n ${PREFIX}-lb-$DEPLID -a $ip
az network dns record-set a update -g speechservicesdevelopmentwestus2 -z develop2.cris.ai --subscription 3a96ef56-41a9-40a0-b0f3-fb125c2b8798 -n speech-loadbalancer-en-us --remove aRecords 0
az network dns record-set a update -g speechservicesdevelopmentwestus2 -z develop2.cris.ai --subscription 3a96ef56-41a9-40a0-b0f3-fb125c2b8798 -n speech-loadbalancer-en-us --add aRecords ipv4Address=$ip
