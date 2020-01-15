#!/bin/bash
############################################################
# Variables
############################################################
# Region does not really matter because the script will iterate through all regions anyways. But a AWS_DEFAULT_REGION
# is required anyways.
AWS_DEFAULT_REGION=eu-west-1

AWS_PROFILE=default
DRY_RUN=False
programname=$0
while getopts ":dhp:" opt; do
  case ${opt} in
    h )
      echo "Usage: $programname [-hd] [-p aws_profile]"
      echo "    -h                 display this help message."
      echo "    -d                 run in DRY-RUN mode."
      echo "    -p aws_profile     specify the AWS profile (by default AWS profile 'default')."
      exit 0
      ;;
    d )
      DRY_RUN=True
      ;;
    p )
      AWS_PROFILE=$OPTARG
      ;;
    \? )
      echo "Invalid option: $OPTARG" 1>&2
      exit 1
      ;;
    : )
      echo "Invalid option: $OPTARG requires an argument" 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

############################################################
# Main
############################################################
docker build -t aws-delete-default-vpcs .

# Creation of directory 'tmp-workaround' is a workaround for running under WSL (Windows Subsystem for Linux).
# This is required due to mapping of volumes for docker not working for directories unless they are located
# on the C: drive.
rm -rf $PWD/tmp-workaround
mkdir $PWD/tmp-workaround
cp $HOME/.aws/credentials $PWD/tmp-workaround/.
cp $HOME/.aws/config $PWD/tmp-workaround/.

docker run -it \
  -v $PWD/tmp-workaround:/root/.aws:ro \
  -e AWS_PROFILE=$AWS_PROFILE \
  -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
  -e DRY_RUN=$DRY_RUN \
  -t aws-delete-default-vpcs

rm -rf $PWD/tmp-workaround
