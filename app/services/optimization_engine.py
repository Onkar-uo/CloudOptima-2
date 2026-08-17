from app.services.csv_store import InMemoryCSVStore

class OptimizationEngine:
    def __init__(self):
        self.store = InMemoryCSVStore()

    def generate_recommendations(self):
        df = self.store.master_df
        actions = []
        if df.empty:
            return [{
                "service": "No Data Loaded",
                "type": "Manual Ingestion Required",
                "description": "Load one or more CSV files from the table on the left.",
                "potential_savings_monthly": 0.00,
                "impact": "Info",
                "action_required": "Click 'Load' on any CSV file."
            }]

        # Group by all loaded services
        service_totals = df.groupby('service')['cost'].sum().to_dict()

        for service, total in service_totals.items():
            if total <= 0:
                continue

            s_upper = service.upper()
            
            # Compute Rules
            if "EC2" in s_upper or "COMPUTE" in s_upper:
                actions.append({
                    "service": service,
                    "type": "Compute Rightsizing & Savings Plans",
                    "description": "Switch steady on-demand instances to 1-Year Compute Savings Plans and evaluate ARM Graviton.",
                    "potential_savings_monthly": round(total * 0.32, 2),
                    "impact": "High",
                    "action_required": "Commit to 1-yr Savings Plans or migrate instances to t4g/c7g tiers."
                })
            # Storage Rules
            elif "S3" in s_upper or "GLACIER" in s_upper:
                actions.append({
                    "service": service,
                    "type": "Storage Lifecycle Rules",
                    "description": "Implement S3 Lifecycle policies to transition objects unaccessed for >90 days to Glacier Deep Archive.",
                    "potential_savings_monthly": round(total * 0.45, 2),
                    "impact": "Medium",
                    "action_required": "Configure bucket lifecycle transition rules."
                })
            # Database Rules
            elif "RDS" in s_upper or "AURORA" in s_upper or "DATABASE" in s_upper:
                actions.append({
                    "service": service,
                    "type": "Database Scheduling & Instance Tuning",
                    "description": "Schedule automatic shutdown for non-prod databases outside working hours and disable Multi-AZ in staging.",
                    "potential_savings_monthly": round(total * 0.28, 2),
                    "impact": "High",
                    "action_required": "Deploy AWS Instance Scheduler Lambda for dev/test databases."
                })
            # Serverless / Lambda Rules
            elif "LAMBDA" in s_upper:
                actions.append({
                    "service": service,
                    "type": "Memory & Execution Timeout Tuning",
                    "description": "Optimize Lambda allocated memory using AWS Lambda Power Tuning to minimize GB-seconds billed.",
                    "potential_savings_monthly": round(total * 0.20, 2),
                    "impact": "Low",
                    "action_required": "Run memory profiling on high-invocation functions."
                })
            # Networking / Load Balancing
            elif "ELB" in s_upper or "VPC" in s_upper or "NAT" in s_upper:
                actions.append({
                    "service": service,
                    "type": "Idle Gateway & ELB Cleanup",
                    "description": "Audit idle NAT Gateways and Elastic Load Balancers receiving zero active traffic.",
                    "potential_savings_monthly": round(total * 0.50, 2),
                    "impact": "Medium",
                    "action_required": "Remove unused VPC endpoints and orphaned target groups."
                })
            # Observability & Logging
            elif "CLOUDWATCH" in s_upper or "LOGS" in s_upper:
                actions.append({
                    "service": service,
                    "type": "Log Retention Policy",
                    "description": "Set explicit log retention periods (30 to 90 days) instead of 'Never Expire'.",
                    "potential_savings_monthly": round(total * 0.35, 2),
                    "impact": "Low",
                    "action_required": "Enforce log group expiration policies."
                })
            # Generic FinOps Heuristic for Any Other Service
            else:
                actions.append({
                    "service": service,
                    "type": "Spend Anomaly & Tag Governance",
                    "description": f"Enforce cost allocation tags and review unblended usage rates for {service}.",
                    "potential_savings_monthly": round(total * 0.15, 2),
                    "impact": "Low",
                    "action_required": "Audit resource usage tags and eliminate unused instances."
                })

        return actions