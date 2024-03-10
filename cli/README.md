# WAFFLE CLI

## Getting started

### Installation


## Terminology

### "deployment"

### deployment ID

### AWS profile

### Cloudformation Stack


## Quickstart: new deployment from scratch


### Creating a settings file

First create the settings file locally. The settings file will be created
in the current `.waffle` folder: it's going to be a `.json` file with the chosen deployment id.

For the choice of `deployment id` check out the terminology above for detailed explanation. Here well use `dev` in the examples below.

```bash
waffle create_deployment_settings dev DEV
```

### AWS credentials for the AWS account to deploy to

```bash
waffle configure_aws_profile dev
```

### Deploy DNS settings and SSL certification

```bash
waffle configure_deployment_domain dev dev.example.com
```

```bash
waffle create_deployment_certificate dev
```

### Deploy foundational stacks

```bash
waffle deploy_vpc dev
```

```bash
waffle deploy_auth dev
```

```bash
waffle deploy_api dev
```



# TODO

CICD trigger:
- with HTTP endpoint + limited api key
- AWS API + creating limited IAM user with access tokens

Notes:
- ECS service port hardcoded to 80
- DB alarms:
    - free storage alarm at 5GB
    - freeable mem at 10MB