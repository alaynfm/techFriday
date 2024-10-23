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
- **TechFridayCode**: A less vulnerable application designed for development purposes.

> [!CAUTION] 
> These are intentionally vulnerable resources. **DO NOT** deploy them in a **ANY** unsupervised environment.

### THE PIPELINE

There is only one pipeline and it will execute a static analysis in the different inrastructure code.  To select different project when executing manually the pipeline the input branch can be selected

- KaiMonkey: `aws KaiMonkey`
- TerraGoat: `aws terragoat` || `az terragoat`
- AWSGoat: `aws` 
- AzureGoat: `az` 
- TechFridayCode: `dev` 

#### Why different branches? 

All the tools that are going to be analyzed upload SARIF reports to GITHUB SECURITY.

SARIF (Static Analysis Results Interchange Format) is an OASIS Standard that defines an output file format. The SARIF standard is used to streamline how static analysis tools share their results. 

In GitHub Security, all reports are uploaded to the same [section](https://github.com/alaynfm/techFriday/security/code-scanning) and can be filtered by tool and branch. To separate the different results, different branches have been created.

#### Pipeline Stages

- CHECK for Secrets: It is imporant to check the security and quelity tool of the terraform code, without forgeting the repository security aside ;)
- Code Linters: Avoid typos, ...
    - TFLINT
- Terraform Static code Analysis Tool:
    - CHECKOV
    - TFSEC
    - SONAR
    - TERRASCAN (Q4 2024)

### Tools Analysis

All the results are uploaded in SARIF format. This are json format, so they can be analyze. To me more visual a `.ypnb notebook` has been created. 

The notebook gets the last pipeline effective executions pipeline of the github.

