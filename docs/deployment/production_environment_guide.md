# AI Artist System Production Environment Guide

This guide provides recommendations and considerations for setting up a production environment for the AI Artist System.

## 1. Overview

Deploying the AI Artist System to production requires careful planning around infrastructure, scalability, security, and maintainability. This guide builds upon the local Docker Compose setup and deployment preparations completed in Phase 3, offering suggestions for a robust production environment.

The target architecture involves running the containerized application components (API, workers) on a container orchestration platform, connected to a production-grade database and supported by monitoring, logging, and CI/CD systems.

## 2. Infrastructure Recommendations

Choosing a cloud provider (AWS, GCP, Azure) often simplifies management through managed services.

*   **Container Orchestration:**
    *   **Recommendation:** Managed Kubernetes (EKS, GKE, AKS) provides scalability, resilience, and a rich ecosystem.
    *   **Alternatives:** Docker Swarm (simpler but less feature-rich), managed container services (AWS ECS, Google Cloud Run - may require adaptation).
*   **Database (PostgreSQL):**
    *   **Recommendation:** Managed PostgreSQL service (AWS RDS, Google Cloud SQL, Azure Database for PostgreSQL). Offers automated backups, patching, scaling, and high availability options.
    *   **Alternatives:** Self-hosting PostgreSQL on virtual machines (requires significant operational overhead).
*   **Container Registry:**
    *   **Recommendation:** Cloud provider registry (ECR, GCR, ACR) or Docker Hub (consider rate limits/costs for private images).
*   **Load Balancer:**
    *   **Recommendation:** Cloud provider load balancer (ALB, ELB, Google Cloud Load Balancer, Azure Load Balancer) to distribute traffic to the API service instances.
*   **Networking (VPC):**
    *   Set up a Virtual Private Cloud (VPC) with private and public subnets.
    *   Place database instances in private subnets, accessible only from application subnets.
    *   Configure security groups/firewall rules to restrict traffic strictly (e.g., allow HTTPS only to the load balancer, allow API access to the database port).
*   **DNS:** Configure DNS records to point your desired domain name to the load balancer.

## 3. Resource Sizing (Initial Estimates)

Resource requirements depend heavily on actual usage patterns. Start with modest resources and scale based on monitoring.

*   **API Service (per instance):**
    *   **CPU:** 1-2 vCPU
    *   **Memory:** 2-4 GB RAM (adjust based on LLM usage and data processing needs)
    *   **Instances:** Start with 2-3 instances behind a load balancer for high availability and scale horizontally based on load.
*   **Worker Service (per instance, if applicable):**
    *   Sizing depends on the tasks (data pipelines, evolution jobs). May require more CPU or memory depending on the workload.
    *   Consider running workers as separate deployments scaled independently.
*   **Database (PostgreSQL):**
    *   **Recommendation:** Start with a small-to-medium managed instance (e.g., db.t3.medium on RDS, db-f1-micro/small on Cloud SQL).
    *   Monitor CPU, memory, IOPS, and connections. Scale vertically (instance size) or horizontally (read replicas) as needed.
    *   Ensure sufficient storage allocated with room for growth.
*   **Monitoring Services (Prometheus/Grafana):**
    *   Sizing depends on metric volume and retention. Managed monitoring services might be simpler.

## 4. Database Configuration (Production)

*   **Use Managed Service:** Strongly recommended for backups, HA, patching.
*   **High Availability:** Configure multi-AZ deployment for automatic failover.
*   **Backups:** Ensure automated daily backups are enabled with appropriate retention periods (e.g., 7-30 days).
*   **Connection Pooling:** Use a connection pooler (like PgBouncer) if the application generates a very high number of connections, although `psycopg2` pooling might suffice initially.
*   **Security:** Use strong passwords, restrict network access, consider encrypting data at rest and in transit.

## 5. Monitoring & Logging (Production)

*   **Centralized Logging:** Ship container logs (stdout/stderr) to a centralized system (CloudWatch Logs, Google Cloud Logging, Azure Monitor Logs, ELK stack, Grafana Loki).
*   **Application Performance Monitoring (APM):** Use Prometheus/Grafana (as set up) or cloud provider tools (CloudWatch, Google Cloud Monitoring, Azure Monitor) or dedicated APM solutions (Datadog, New Relic).
*   **Key Metrics:** Monitor API latency/error rates, request throughput (RPS), database performance (CPU, memory, IOPS, connections, query latency), container resource usage (CPU, memory), LLM API usage/latency/costs.
*   **Alerting:** Configure alerts based on key metrics (e.g., high error rates, high latency, low disk space, high resource utilization) to notify operations teams.

## 6. Secret Management (Production)

*   **DO NOT** store secrets directly in configuration files, code, or unencrypted environment variables in production.
*   **Recommendation:** Use a dedicated secret management system:
    *   HashiCorp Vault
    *   AWS Secrets Manager
    *   Google Cloud Secret Manager
    *   Azure Key Vault
*   Inject secrets securely into the container environment at runtime (e.g., mounted as files/volumes, injected as environment variables by the orchestrator).

## 7. Deployment Strategy

*   **CI/CD:** Utilize the established CI/CD pipeline (GitHub Actions) to automate testing, building, and potentially deployment.
*   **Image Tagging:** Use semantic versioning or Git commit SHAs for Docker image tags.
*   **Deployment Methods:**
    *   **Rolling Updates:** Gradually replace old instances with new ones (supported by Kubernetes/ECS).
    *   **Blue-Green Deployment:** Deploy the new version alongside the old one, switch traffic once validated.
*   **Database Migrations:** Run Alembic migrations (`migrate_db.sh` or equivalent CI/CD step) *before* deploying the new application code that depends on the schema changes. Ensure backward compatibility where possible or plan for brief maintenance windows.

## 8. Security Hardening

*   **OS/Base Image:** Use minimal, hardened base images for containers. Regularly update base images and dependencies to patch vulnerabilities (use Trivy scanning in CI/CD).
*   **Container Security:** Run containers as non-root users (as implemented in the Dockerfile). Use security contexts in Kubernetes.
*   **Network Security:** Strictly configure firewalls/security groups.
*   **API Security:** Implement authentication/authorization if the API needs to be protected. Use HTTPS for all external communication.
*   **Regular Audits:** Periodically perform security audits and vulnerability scans.

This guide provides a starting point. Adapt these recommendations based on your specific requirements, chosen infrastructure, and operational practices.

