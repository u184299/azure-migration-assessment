\# Migration Post-Mortem, Risk Matrix, \& Modernization Roadmap



\## 1. Core Engineering Assumptions \& Limitations

\* \*\*Assumptions:\*\* Network transit capacity between the on-premises datacenter and Azure over the ExpressRoute circuit will maintain a minimum available bandwidth of 1 Gbps during data synchronization.

\* \*\*Limitations:\*\* The secondary Python/FastAPI codebase utilizes local file persistence strategies for transient request storage; this must be refactored to use shared Azure Files mount points during Phase 2.



\## 2. Hypercare \& Day-2 Operational Governance

\* \*\*Hypercare Support Window:\*\* 14 Days post-migration with dedicated 24/7 engineering war rooms.

\* \*\*Telemetry \& Monitoring Gates:\*\*

&#x20; \* \*\*Azure Monitor Logs:\*\* Aggregating runtime stdout streams through your dedicated Log Analytics Workspace.

&#x20; \* \*\*Alerting Thresholds:\*\* Immediate escalations triggered if container restarts exceed 3 within a rolling 15-minute window or if database CPU utilization trends past 85%.



\## 3. Future-State Architectural Roadmap (Evolutionary Blueprint)

&#x09;	  \[ Phase 1: Replatform (Current Target) ]

&#x20;                                     │

&#x20;                    Deploy to Azure Container Apps (ACA)

&#x20;                Managed Flexible Database Tiers (MySQL/Postgre)

&#x20;                                     │

&#x20;                                     ▼

&#x20;                  \[ Phase 2: Native Microservices Optimization ]

&#x20;                                     │

&#x20;               Extract Monolith Domains to Isolated API Services

&#x20;              Transition Shared Environments from ACA to Azure AKS

&#x20;                                     │

&#x20;                                     ▼

&#x20;                    \[ Phase 3: Zero-Trust Security ]

&#x20;                                     │

&#x20;                Inject Identities via Managed Identities (MSI)

&#x20;               Enforce Secret Hardening using Azure Key Vault (AKV)

\### Milestone 1: Zero-Trust Security Enhancements (Short-Term)

\* \*\*Action:\*\* Eliminate cleartext environment string database connections from the `docker-compose.yml` and Bicep runtime profiles.

\* \*\*Implementation:\*\* Inject secrets securely at runtime using native \*\*Azure Key Vault\*\* integration paired with \*\*User-Assigned Managed Identities\*\* across all containers.



\### Milestone 2: Transition to Azure Kubernetes Service (AKS) (Medium-Term)

\* \*\*Action:\*\* Evaluate moving away from Azure Container Apps once the portfolio extends past 15 discrete, interacting service workloads.

\* \*\*Implementation:\*\* Standardize container orchestration using an \*\*Azure Kubernetes Service (AKS)\*\* topology utilizing an Azure Application Gateway Ingress Controller (AGIC) to achieve granular layer-7 traffic control.

