# aws-delete-default-vpcs

The default VPCs come with a default security group whose initial settings are too open with respect to security,
see [Compliance Standards: CIS AWS Foundations](https://docs.aws.amazon.com/securityhub/latest/userguide//securityhub-standards.html). 

A simple fix is to delete the default VPCs in all regions when setting up a new AWS account.
Below script does this. It will also delete all dependencies of the default VPCs, i.e.: 
* default subnets.
* IGWs.

## Prerequisites

In order to connect to a certain AWS account please provide the following environment variables:

```
export AWS_DEFAULT_REGION=<...>
export AWS_SECRET_ACCESS_KEY=<...>
export AWS_ACCESS_KEY_ID=<...>
```

## Run

### Make a DRY-RUN

By default the script will only do a _**DRY RUN**_, i.e. it will show which resources it would delete.

Run the script by means of:

```
./run.sh
```

### Make a NON-DRY-RUN

If the script is to be run for real then change the flag `DRY_RUN` to `False` 
in [delete-default-vpcs.py](./delete-default-vpcs.py) and rerun the script.

```
DRY_RUN = False
```

If the script for some reason does not succeed to delete the default VPC then the most likely cause is that other 
resources have been created inside this VPC and block the deletion. 

In this case please delete the VPC manually through the console. 
After that rerun the script in order to confirm that the default VPCs do no longer exist.  
