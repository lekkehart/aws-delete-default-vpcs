# aws-delete-default-vpcs

The default VPCs come with a default security group whose initial settings are too open with respect to security,
see [Compliance Standards: CIS AWS Foundations](https://docs.aws.amazon.com/securityhub/latest/userguide//securityhub-standards.html). 

A simple fix is to delete the default VPCs in all regions when setting up a new AWS account.
Below script does this. It will also delete all dependencies of the default VPCs, i.e.: 
* default subnets.
* IGWs.

## Run

There are some command line options when running the script:
* Run in _**DRY RUN**_ mode, i.e. it will show which resources it would delete.
* Specify the AWS profile to use. 

```
./run.sh -h
Usage: ./run.sh [-hd] [-p aws_profile]
    -h                 display this help message.
    -d                 run in DRY-RUN mode.
    -p aws_profile     specify the AWS profile (by default AWS profile 'default').
```

By default, the script will run in NON-DRY-RUN mode using AWS profile `default`.

```
./run.sh
```

### Actions if Script Fails

If the script for some reason does not succeed to delete the default VPC then the most likely cause is that other 
resources have been created inside this VPC and block the deletion. 

In this case please delete the VPC manually through the console. 
After that rerun the script in order to confirm that the default VPCs do no longer exist.  
