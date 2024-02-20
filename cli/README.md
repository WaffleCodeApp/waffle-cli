# WAFFLE CLI

## Getting started

### Installation


## Terminology

### "deployment"

### deployment ID

### AWS profile

### Cloudformation Stack


## Creating a new deployment from scratch


### Creating a settings file

First create the settings file locally. The settings file will be created
in the current `.waffle` folder: it's going to be a `.json` file with the chosen deployment id.

For the choice of `deployment id` check out the terminology above for detailed explanation. Here well use `dev` in the examples below.

```bash
waffle create_new_deployment dev
```

```bash
waffle set_deployment_type dev DEV
```

### AWS credentials for the AWS account to deploy to

```bash
waffle configure_aws_profile dev
```

### Deploy DNS settings and SSL certification

```bash
waffle configure_deployment_domain dev
```

```bash
waffle create_deployment_certificate dev
```
