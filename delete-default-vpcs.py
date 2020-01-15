#!/usr/bin/env python
import json
import logging
import os
import sys

import boto3
# initialise logger
from botocore.exceptions import ClientError

DRY_RUN = True
if os.environ.get('DRY_RUN') == 'False':
    DRY_RUN = False

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)


def get_regions(client):
    """ Build a region list """

    reg_list = []
    regions = client.describe_regions()
    data_str = json.dumps(regions)
    resp = json.loads(data_str)
    region_str = json.dumps(resp['Regions'])
    region = json.loads(region_str)
    for reg in region:
        reg_list.append(reg['RegionName'])
    return reg_list


def get_default_vpcs(client):
    vpc_list = []
    vpcs = client.describe_vpcs(
        Filters=[
            {
                'Name': 'isDefault',
                'Values': [
                    'true',
                ],
            },
        ]
    )
    vpcs_str = json.dumps(vpcs)
    resp = json.loads(vpcs_str)
    data = json.dumps(resp['Vpcs'])
    vpcs = json.loads(data)

    for vpc in vpcs:
        vpc_list.append(vpc['VpcId'])

    return vpc_list


def delete_igw(ec2_resource, vpc_id):
    """ Detach and delete the internet-gateway """
    vpc_resource = ec2_resource.Vpc(vpc_id)
    igws = vpc_resource.internet_gateways.all()
    if igws:
        for igw in igws:
            try:
                log.info("Detaching and deleting IGW ID: {}".format(igw.id))
                if not DRY_RUN:
                    igw.detach_from_vpc(VpcId=vpc_id)
                    igw.delete()
            except ClientError as e:
                log.error("Failed to delete IGW.")
                raise


def delete_default_subnets(ec2, vpc_id):
    """ Delete the default subnets """
    vpc_resource = ec2.Vpc(vpc_id)
    subnets = vpc_resource.subnets.all()

    for subnet in subnets:
        if subnet.default_for_az:
            try:
                log.info("Deleting Default Subnet ID: {}".format(subnet.id))
                if not DRY_RUN:
                    subnet.delete()
            except ClientError as e:
                log.error("Failed to delete subnet.")
                raise


def delete_vpc_dependencies(ec2_resource, vpc_id):
    """ Delete the VPC dependencies"""
    delete_default_subnets(ec2_resource, vpc_id)
    delete_igw(ec2_resource, vpc_id)


def delete_vpc(ec2_resource, vpc_id):
    """ Delete the VPC """
    delete_vpc_dependencies(ec2_resource, vpc_id)

    vpc_resource = ec2_resource.Vpc(vpc_id)
    try:
        log.info("Deleting VPC ID: {}".format(vpc_resource.id))
        if not DRY_RUN:
            vpc_resource.delete()
    except ClientError as e:
        log.error("Failed to delete VPC.")
        raise


def main():
    ec2_client_1 = boto3.client('ec2')
    regions = get_regions(ec2_client_1)

    for region in regions:
        log.info('=' * 75)
        log.info("REGION: {}".format(region))
        try:
            ec2_client_2 = boto3.client('ec2', region_name=region)
            ec2_resource = boto3.resource('ec2', region_name=region)
            default_vpcs = get_default_vpcs(ec2_client_2)
        except boto3.exceptions.Boto3Error as e:
            log.exception(e)
            exit(1)
        else:
            for default_vpc in default_vpcs:
                log.info('.' * 75)
                log.info("Default VPC Id: {}".format(default_vpc))
                delete_vpc(ec2_resource, default_vpc)


def print_note(msg):
    log.info('!' * 75)
    log.info('!' * 75)
    log.info('!' * 75)
    log.info(msg)
    log.info('!' * 75)
    log.info('!' * 75)
    log.info('!' * 75)


if __name__ == "__main__":
    if DRY_RUN:
        print_note('START - DRY-RUN only!')
    else:
        print_note('START')

    main()

    if DRY_RUN:
        print_note('END - DRY-RUN only!')
    else:
        print_note('END')
