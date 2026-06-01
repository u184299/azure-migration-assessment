\# Enterprise Migration Cutover \& Rollback Playbook



\## 1. Maintenance Window Profile

\* \*\*Target Window Duration:\*\* 4 Hours (Sunday 01:00 AM – 05:00 AM UTC)

\* \*\*Maximum Allowable Downtime (RTO):\*\* 30 Minutes

\* \*\*Data Loss Tolerance (RPO):\*\* 0 Minutes (Strict zero-data-loss requirement)



\## 2. Phase-by-Phase Execution Sequence



\### Phase A: Pre-Cutover Validation (T-Minus 24 Hours)

| Sequence | Action Item | Responsibility | Verification Command / Metric |

| :--- | :--- | :--- | :--- |

| A.01 | Verify CI/CD container artifact replication across ACR | DevOps Engineer | `az acr repository list --name acrenterprisemigrationprod001` |

| A.02 | Perform final transactional smoke tests on on-prem databases | Lead DBA | Check local transaction counts \& error rates |



\### Phase B: Execution Window \& Data Catch-Up (T-Hour)

| Sequence | Action Item | Responsibility | Execution Command / Notes |

| :--- | :--- | :--- | :--- |

| B.01 | Place on-premises monolith application into Read-Only mode | App Team | Inject maintenance splash page banner; redirect traffic |

| B.02 | Freeze upstream write queues and flush remaining transactional data | Lead DBA | `FLUSH TABLES WITH READ LOCK;` (MySQL instance) |

| B.03 | Initiate final delta data sync to Azure Database Flexible Servers | Cloud Migration Eng | Execute Azure Migrate replication catch-up sync sync |

| B.04 | Confirm data synchronization consistency and record row counts | Lead DBA | Compare target vs source checksum totals |



\### Phase C: Cloud Runtime Activation (T-Plus 1 Hour)

| Sequence | Action Item | Responsibility | Verification Mechanism |

| :--- | :--- | :--- | :--- |

| C.01 | Release database write locks on Azure Flexible Servers | Lead DBA | Verify read/write permissions for `cloudadmin` user |

| C.02 | Trigger the delivery pipeline to activate Azure Container Apps | DevOps Engineer | Confirm HTTP 200 state via Private Ingress endpoints |

| C.03 | Update core DNS records to point to the Azure Front Door VIP | Traffic Manager | `nslookup petclinic.enterprise.com` |



\---



\## 3. Rollback \& Contingency Framework



\### Rollback Triggers

\* Data synchronization validation fails or exhibits corruption that cannot be resolved within 45 minutes of the migration window.

\* Azure Container Apps platform runtime experiences a persistent crash looping state (`HTTP 503` or failing internal health check probes) exceeding 20 minutes.



\### Action Plan (Reverting to On-Premises Baseline)

```bash

\# 1. Immediate traffic rerouting: Roll back the primary DNS record pointer to the on-prem VIP

az network traffic-manager profile update --name tm-prod-profile --set dnsConfig.ttl=60



\# 2. Re-enable write-access mode on the local on-prem VMware cluster instances

ssh admin@onprem-app-monolith "sudo systemctl restart spring-petclinic"



\# 3. Purge or isolate failed cloud transaction fragments to avoid downstream cache collisions

\# 4. Notify the Change Advisory Board (CAB) of window closure and schedule a post-mortem review

