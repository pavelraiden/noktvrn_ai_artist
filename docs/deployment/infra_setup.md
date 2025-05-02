# Vultr Infrastructure Setup Plan (Phase 10.1)

This document outlines the proposed infrastructure setup on Vultr for the AI Artist Platform, designed to support 100-300 concurrent artists.

## 1. Hosting Provider

**Provider:** Vultr (Selected based on user instruction due to pre-payment).
**Reference:** `docs/deployment/provider_selection.md`

## 2. Core Components & Requirements

*   **Backend Application:** Python-based (Flask, LLM Orchestrator, Batch Runner, API Clients, etc.). Requires sufficient CPU/RAM for concurrent processing, LLM interactions, and API calls for potentially hundreds of artists.
*   **Frontend Dashboard:** Flask-based UI for administration and artist lifecycle control (Start/Pause). Relatively lightweight but needs reliable hosting.
*   **Database:** PostgreSQL required for storing artist profiles, metrics, release data, configuration, etc. Needs high availability, automated backups, and scalability.
*   **File Storage:** Storage for generated media assets (audio, video, images). Needs to be scalable, durable, and cost-effective.
*   **Networking:** Secure network configuration, potentially including private networking, load balancing, and firewall rules.
*   **Scalability:** Infrastructure must support scaling from 100 to 300+ artists.
*   **Security:** API keys managed via `.env`, secure database access, firewall rules, potential basic auth for dashboard.

## 3. Proposed Vultr Infrastructure

Based on Vultr product offerings and general cloud best practices, the following setup is proposed:

*   **Compute Instances (Backend/Orchestrator):**
    *   **Type:** Vultr Optimized Cloud Compute (Cloud GPU instances might be considered later if heavy ML/inference tasks are added locally, but current LLM usage is API-based).
    *   **Initial Size:** Start with 1-2 instances of `vc2-4c-8gb` (4 vCPU, 8GB RAM). This provides a balance of CPU/RAM for the Python backend processes.
    *   **Scaling:** Utilize Vultr Load Balancers to distribute traffic if using multiple instances. Autoscaling groups can be configured based on CPU/memory metrics, adding/removing instances as needed to handle the artist load. Start/Pause logic should reduce load significantly for paused artists.
    *   **Rationale:** Optimized instances offer better performance for demanding applications compared to standard compute. Starting with a moderate size allows for cost control, with clear scaling paths.

*   **Compute Instance (Frontend Dashboard):**
    *   **Type:** Vultr High Frequency Compute or Regular Performance.
    *   **Size:** A smaller instance like `hf-1c-1gb` (1 vCPU, 1GB RAM) or `vc2-1c-2gb` (1 vCPU, 2GB RAM) should suffice for the Flask admin UI.
    *   **Rationale:** The frontend is expected to have lower resource demands than the backend.

*   **Managed Database (PostgreSQL):**
    *   **Type:** Vultr Managed Database for PostgreSQL.
    *   **Initial Plan:** Start with a 2 vCPU, 4GB RAM plan with 3 nodes (1 primary, 2 standbys) for High Availability. Storage starting at ~80-100GB (adjust based on estimated data per artist).
    *   **Features:** Automated backups, automatic failover, vertical scaling (upgrade plan size), read replicas (optional for scaling read load).
    *   **Rationale:** Managed service reduces operational overhead. High Availability is crucial for production. Vertical scaling allows easy upgrades as data/load grows. Pricing starts around $60/month for a 3-node HA cluster (based on general Vultr pricing, specific plan details might vary).

*   **File Storage:**
    *   **Type:** Vultr Object Storage.
    *   **Usage:** Store all generated media assets (audio, video, images).
    *   **Rationale:** Highly scalable, durable, and cost-effective for large amounts of unstructured data compared to block storage. Pricing is typically per GB stored and GB transferred.

*   **Networking:**
    *   **VPC:** Deploy instances within a Vultr VPC for private networking between components (e.g., backend accessing database).
    *   **Load Balancer:** Use Vultr Load Balancer if deploying multiple backend instances for scalability and availability.
    *   **Firewall:** Configure Vultr Firewall rules to restrict access to necessary ports (e.g., allow HTTPS to frontend/LB, restrict DB access to VPC internal IPs).

## 4. Estimated Monthly Cost (Rough Estimate)

*   Backend Instance(s) (Optimized `vc2-4c-8gb` @ ~$48/mo each): $48 - $96 (1-2 instances)
*   Frontend Instance (`hf-1c-1gb` @ ~$6/mo): $6
*   Managed PostgreSQL (HA, 2vCPU/4GB RAM, ~100GB): ~$60 - $100 (Estimate based on typical managed DB pricing)
*   Object Storage (Estimate 500GB): ~$5 (Vultr Object Storage is often around $5/250GB, estimate may vary)
*   Load Balancer (If used): ~$10/mo
*   **Total Estimated Range:** **~$129 - $217 per month** (excluding bandwidth overages, which depend on usage).

*Note: These are rough estimates based on publicly available information and typical Vultr pricing structures. Actual costs depend on selected regions, specific plan details at the time of deployment, and actual resource consumption.* 

## 5. Security Considerations

*   Use Vultr Firewall to limit access.
*   Store all credentials (DB password, API keys) securely in `.env` files, not in code.
*   Use strong passwords for database and instance access.
*   Implement HTTPS for the frontend dashboard.
*   Consider adding Basic Authentication or more robust user authentication to the Flask admin dashboard.
*   Regularly update server OS and dependencies.

## 6. Deployment Strategy

*   Utilize Docker and Docker Compose for containerizing the backend application, frontend, and potentially other services.
*   Store deployment configurations (Docker Compose files, setup scripts) in the `/deployment/` directory.
*   Automate infrastructure provisioning using tools like Terraform or Vultr's API/CLI if possible in the future.

