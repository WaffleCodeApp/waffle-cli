---
title: Introduction
---

# Waffle CLI

Waffle helps one deploy a secrure foundation for web applications and host their backend and frontend components using AWS.

To deploy a sample application to your AWS account, checkout the [Quickstart](quickstart). To deploy your own project, refer to [Get Started](get_started/index).

## What is Waffle?

"Waffle" is a set of tools that help web-application developers kick off new projects or move existing projects quickly in a secure, scalable, easily reproducible, audit- and pentest-ready cloud environment without requiring devops expertise.

Waffle exclusively builds on AWS. It sets up and configures native AWS components in a way that's suitable for regular B2B web-applications. It can also be used for backend/API only solutions too.

Waffle help one build a complex cloud infrastructure with losely connected templates that interact with each other. These templates are written for AWS CloudFormation. They deploy AWS components with default values, designed for the purpose.

The default settings provided by Waffle can be manually tweaked.  Waffle is open source. Its templates can be altered or completely replaced too if the project that Waffle is used for develops requirements that Waffle doesn't support out of the box. 3rd party CloudFormation templates also perfectly work together with Waffle's templates. 

## Why Waffle?

To kick off a B2B web-project it's hard (if possible at all) to meet all the usual requirements without Waffle. These are:

- Kicking off the project fast and cheap in small-scale for validation and early-stage growth.
- Enable a high level of security to earn business partners' trust.
- Enable scaling.

### Alternatives to Waffle.

There are many:

- **AWS, Azure:** Working with low-level infrastructure-as-services like AWS or Azure require a high level of related expertise. It doesn't only take way too much time to build a suitable cloud infrastructure compared to the webapplication that's being hosted, but you also need to pay for the related engineering. This is approach is suitable if you already have a strong devops and infrastructure team. What you might miss from the goals above: kicking off fast and cheap.
- **AWS SAM:** although we can think about it as a simplification-layer for building applicaitons with serverless cloud infrastructure, it still requires significant AWS-specific expertise. And serverless is often not the best choice for a project in the validation-phase. This solution is suitable if you already have engineers with an AWS background and your project best developed for serverless right from the beginning. What you might miss: kicking off fast and cheap.
- **Digital Ocean, Heroku:** These platform-as-service solutions provide backend services that are similarly easy to set up as doing it with Waffle. They also provide dashboards and control interfaces that are easy to work with without being an infrastructure expert. These solutions' pricing model is designed for small-scale projects. If your project scales up, then the price likely goes up as well. You'll face a decision if you rewrite your project for an infrastructure that better supports scaling, or accept the higher costs. These services are mostly suitable for teams without deep infrastructure and devops related expertise and without planning to scale significantly up. What you might miss: enabling scaling.
- **Supabase:** It's a collection of great 3rd party open source projects that you can host on your own, or leave hosting to Supabase. Projects built with Supabase require very specific implementations to these opensource projects. Scalability is limited to how you can deploy these 3rd party solutions and to these solutions themselves. You should examine these tools before you commit to using them. If they fit, it can be a great choice for you. What you might miss: if deployed to your own premises or AWS private cloud, then security (and scaling) might be a concern.
- **BYO Linux server:** While this can be a very fast and cheap way to develop and deploy new applications, implementing CICD pipelines and other devops practices that are required for generic compliance can be more than tricky. This can be suitable option if you have a team of max 1-2 engineers.

### The goals of Waffle

- Leveraging the flexibilityand scalability to AWS, by only relying on AWS native components and solutions.
- Providing default setup and settings for AWS components to provide high-level, industry-standard security suitable for basic projects, without having to do the research.
- Providing a simple way of configuring and deploying components by working with pre-built stack-templates that can be deployed with a basic backend-engineer knowledge.
- No lock-in: only providing solutions that can smoothly work with custom or 3rd party solutions designed for AWS.
- Open source: the templates and defaults provided by Waffle can be tweaked, changed or completely replaced without major refactoring.
- Supporting industry-best practices for backend and api development.
- Logging and monitoring out of the box, compliant with SOC II Type 2.

### When not to use Waffle?

Working with Waffle will require you to work with the AWS console. Just instead of figuring it out how it works, things will be set up for you by Waffle. If you don't think you'll project will ever require the components, security and scalability provided by AWS, then Waffle might be an overkill for you.
