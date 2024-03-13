---
title: Quickstart
description: Setting up a cloud environment from scratch
---

# Waffle CLI Quickstart

The Waffle CLI keeps track of every deployment created with it in a local config file. Creating a deployment means that a settings file is created, and AWS components are created based on the settings using CloudFormation. It's possible to change the settings later on, the Waffle CLI can invoke AWS CloudFormation to update the existing AWS components accordingly.

The idea is that the settings files should be added to a repository. It can be either an isolated repo, or part of a monolith repo that holds the rest of the project.

## Installing the Waffle CLI

```bash
pip install waffle-cli
```

## Creating a settings file

First create the settings file locally. The settings file will be created
in the current `.waffle` folder: it's going to be a `.json` file with the chosen deployment id.

For the choice of `deployment id` check out the terminology above for detailed explanation. Here well use `dev` in the examples below.

```bash
waffle create_deployment_settings dev DEV
```

## Setting up a local AWS profile

```bash
waffle configure_aws_profile dev
```

## Deploying DNS settings and SSL certification

```bash
waffle configure_deployment_domain dev dev.example.com
```

```bash
waffle create_deployment_certificate dev
```

## Deploying foundational stacks

```bash
waffle deploy_vpc dev
```

```bash
waffle deploy_auth dev
```

```bash
waffle deploy_api dev
```

```bash
waffle deploy_alerts dev
```

```bash
waffle deploy_github dev
```

```bash
waffle deploy_deployment dev
```
