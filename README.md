# #TECH_FRIDAY  ![Techie](https://awesome.re/badge.svg)
 
Welcome to the Infrastructure Deployment Laboratory! 

![USED](https://skillicons.dev/icons?i=terraform,aws,azure,python)


The objective of this laboratory is to experiment with various Infrastructure as Code (IaC) tools to enhance Terraform code by incorporating industry best practices.

The objective is not to replace cloud controls. The final approval for deploying infrastructure should remain within the cloud provider. **Why?**

Cloud providers have their own rules, which can be categorized into two types:
- **Preventive:** Prevents unauthorized deployments.
- **Detective:** Detects issues post-deployment.

If deployment controls are placed within the repository code, bypassing these controls could allow unauthorized deployments, leaving the environment unmonitored.

> [!IMPORTANT] 
> The primary aim of this repository is to enhance the quality of Terraform code, ensuring security adoption is made at the early stages of infrastructure creation.
>
> The intention is not to replace existing cloud governance (which is crucial).

### What Infrastructure Will Be Used?

The scope includes only AWS and Azure public clouds. To determine the most suitable tool, various vulnerable infrastructures will be utilized:

- **[KaiMonkey](https://github.com/tenable/KaiMonkey)**: Designed to test AWS security configurations.
- **[TerraGoat](https://github.com/octodemo/advanced-security-terraform)**: A vulnerable infrastructure for both AWS and Azure, designed to test security configurations.
- **[AWSGoat](https://github.com/ine-labs/AWSGoat)**: A vulnerable infrastructure for AWS.
- **[AzureGoat](https://github.com/ine-labs/AzureGoat)**: Designede for Azure

> [!CAUTION] 
> These are intentionally vulnerable resources. **DO NOT** deploy them in a **ANY** unsupervised environment.

### THE PIPELINE

#### Static Analysis Tools

- CHECKOV
- TFSEC
- SONAR (LOCAL RUNNERS FOR COMMUNITY EDITION)
- TERRASCAN (Q4 2024)

### Tools Analysis

All the results are uploaded in SARIF format. This are json format, so they can be analyze. To me more visual a `.ypnb notebook` has been created. 

The notebook gets the last pipeline effective executions pipeline of the github.

