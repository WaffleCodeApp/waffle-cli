---
title: create_deployment_settings
---

# create_deployment_settings

Creates a new set of settings. This command only creates a settings file locally. Adding different features to it, and actually deploying it to AWS is done by other commands.

Usage:

```bash
waffle create_deployment_settings DEPLOYMENT_ID DEPLOYMENT_TYPE
```

Where:

- `DEPLOYMENT_ID` The deployment id refers to a deployment. The idea is to use waffle in a repository, this case it's a common practice to use the SDLC phase's name that the deployment is used for. It could be for example something like `dev`, `development`, `qa`, `prod`.
 
- `DEPLOYMENT_TYPE` There are two deployment types supported: `DEV` and `PROD`. This setting influences how logging and monitoring is done in AWS. In general in case of `DEV` CloudWatch logs are only retained for a month, and only the most crucial CloudWatch Alarms are set. While in case of `PROD`, the log retention is 365 days, and all alarms are set up that are required for an SOC II Type 2 audit.
