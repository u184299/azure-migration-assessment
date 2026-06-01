import os
import re
import json
import csv
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="ADDM-Style Discovery and Dependency Crawler")
    parser.add_argument("--root", default=".", help="Root directory to scan")
    parser.add_argument("--network-flows", default="inventory/network_flows.csv", help="Path to network flows CSV")
    parser.add_argument("--out", default="inventory", help="Output directory for inventory files")
    return parser.parse_args()

def scan_codebase(app_dir):
    findings = {
        "frameworks": [],
        "ports_found": set(),
        "potential_secrets": 0,
        "db_connection_strings": []
    }
    
    # Static analysis regex signatures
    port_regex = re.compile(r'(?:port|server\.port|PORT)\s*=\s*(\d+)')
    secret_regex = re.compile(r'(?:secret|password|passwd|pwd|key)\s*=\s*["\'][a-zA-Z0-9_\-]+["\']', re.IGNORECASE)
    db_regex = re.compile(r'(jdbc:postgresql|jdbc:mysql|mongodb://|postgresql://)')

    for root, _, files in os.walk(app_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Framework / Build Target Tracking
            if file in ["pom.xml", "build.gradle"]:
                if "Java/Spring Boot Monolith" not in findings["frameworks"]:
                    findings["frameworks"].append("Java/Spring Boot Monolith")
            if file in ["requirements.txt", "main.py"]:
                if "Python/FastAPI API Service" not in findings["frameworks"]:
                    findings["frameworks"].append("Python/FastAPI API Service")

            # Deep Configuration Scanning
            if file.endswith(('.xml', '.properties', '.yml', '.yaml', '.py', '.conf', '.json')):
                try:
                    with open(file_path, 'r', errors='ignore') as f:
                        content = f.read()
                        
                        # Extract ports
                        for p in port_regex.findall(content): 
                            findings["ports_found"].add(p)
                        
                        # Extract DB configurations
                        if db_regex.search(content):
                            findings["db_connection_strings"].append(file)
                        
                        # Flag hardcoded secrets (DevSecOps Baseline Audit)
                        secrets = secret_regex.findall(content)
                        findings["potential_secrets"] += len(secrets)
                except Exception:
                    pass
                    
    findings["ports_found"] = list(findings["ports_found"])
    return findings

def process_network_flows(flow_path):
    ingress, egress, databases = [], [], []
    if not os.path.exists(flow_path):
        return ingress, egress, databases

    with open(flow_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            traffic = row.get("Traffic_Type", "")
            if "Ingress" in traffic:
                ingress.append(row)
            elif "Database" in traffic:
                databases.append(row)
            else:
                egress.append(row)
    return ingress, egress, databases

def generate_mermaid_graph(databases, egress_list):
    mmd = "graph TD\n"
    mmd += "    Client[External Traffic / Ingress Load Balancer] -->|Port 8080/443| AppMonolith[On-Premises Monolith Application Layer]\n"
    
    for db in databases:
        mmd += f"    AppMonolith -->|Database Connection TCP Port {db['Destination_Port']}| DB_{db['Destination_Port']}[({db['Traffic_Type']})]\n"
    for eg in egress_list:
        mmd += f"    AppMonolith -->|Outbound API Integration Port {eg['Destination_Port']}| Ext_{eg['Destination_Port']}[{eg['Traffic_Type']}]\n"
    return mmd

def main():
    args = parse_arguments()
    os.makedirs(args.out, exist_ok=True)
    
    print("[*] Initiating Static Codebase Dependency Discovery Scan...")
    code_findings = scan_codebase(os.path.join(args.root, "app"))
    
    print("[*] Processing ADDM Network Telemetry Logs...")
    ingress, egress, databases = process_network_flows(args.network_flows)
    
    # Structuring Application Inventory Document
    app_inventory = {
        "detected_workloads": code_findings["frameworks"],
        "static_discovered_ports": code_findings["ports_found"],
        "configuration_files_with_db_references": list(set(code_findings["db_connection_strings"])),
        "flagged_hardcoded_secrets_count": code_findings["potential_secrets"]
    }
    
    with open(os.path.join(args.out, "app_inventory.json"), "w") as jf:
        json.dump(app_inventory, jf, indent=4)
        
    # Write Normalized Core Migration Logs
    fieldnames = ["Source_IP", "Source_Port", "Destination_IP", "Destination_Port", "Protocol", "Traffic_Type"]
    
    with open(os.path.join(args.out, "ingress_inventory.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(ingress)
            
    with open(os.path.join(args.out, "egress_inventory.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(egress)

    with open(os.path.join(args.out, "database_inventory.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(databases)

    # Export Mermaid Visual Mapping Code
    mermaid_data = generate_mermaid_graph(databases, egress)
    with open(os.path.join(args.out, "dependency_graph.mmd"), "w") as mf:
        mf.write(mermaid_data)

    print(f"[+] Discovery Processed Successfully! Outputs saved to: .\\{args.out}\\")

if __name__ == "__main__":
    main()