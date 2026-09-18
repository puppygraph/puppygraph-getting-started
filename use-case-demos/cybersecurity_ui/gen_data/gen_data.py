import csv
import random
import ipaddress
import uuid
import os
import time
from datetime import datetime, timedelta

OUTPUT_DIR = "csv_data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

NUM_SUBNETS = 20
NUM_INSTANCES = 5000
MIN_INTERFACES_PER_INSTANCE = 1
MAX_INTERFACES_PER_INSTANCE = 3
MIN_FINDINGS_PER_INSTANCE = 1
MAX_FINDINGS_PER_INSTANCE = 10

# VPC Flow Logs configuration
NUM_EXTERNAL_IPS = 200
NUM_EXTERNAL_FLOWS = 5000
NUM_INTERNAL_FLOWS = 8000
EXTERNAL_FACING_RATIO = 0.15  # 15% of instances are external-facing

REGIONS = ["us-east-1", "us-west-2", "eu-north-1", "ap-southeast-1"]
AVAILABILITY_ZONES = {
    "us-east-1": ["us-east-1a", "us-east-1b", "us-east-1c"],
    "us-west-2": ["us-west-2a", "us-west-2b", "us-west-2c"],
    "eu-north-1": ["eu-north-1a", "eu-north-1b"],
    "ap-southeast-1": ["ap-southeast-1a", "ap-southeast-1b"]
}

def generate_cidr():
    network = ipaddress.IPv4Network("10.0.0.0/16")
    subnets = list(network.subnets(new_prefix=24))
    return str(random.choice(subnets))

# 1. Get CVE data with weighted selection based on base_score^3
cve_data = []
with open("cve.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            base_score = float(row["base_score"]) if row["base_score"] else 0.0
            weight = 3 ** base_score  # Weight is 3^base_score
            cve_data.append({
                "id": row["id"],
                "base_score": base_score,
                "weight": weight
            })
        except ValueError:
            # Skip CVEs with invalid base_score
            continue

# Create weighted selection function
def select_weighted_cve():
    """Select a CVE based on base_score^3 weighting"""
    if not cve_data:
        return "CVE-2021-0001"  # Fallback
    
    total_weight = sum(cve["weight"] for cve in cve_data)
    if total_weight == 0:
        return random.choice(cve_data)["id"]
    
    rand_val = random.uniform(0, total_weight)
    cumulative = 0
    for cve in cve_data:
        cumulative += cve["weight"]
        if cumulative >= rand_val:
            return cve["id"]
    
    return cve_data[-1]["id"]  # Fallback to last CVE

# 2. ec2_subnets.csv
subnets = []
for i in range(NUM_SUBNETS):
    subnet_id = f"subnet-{uuid.uuid4().hex[:16]}"
    region = random.choice(REGIONS)
    cidr_block = generate_cidr()
    available_ip_count = random.randint(50, 254)
    default_for_az = random.choice([True, False])
    map_customer_owned = random.choice([True, False])
    map_public = random.choice([True, False])
    az = random.choice(AVAILABILITY_ZONES[region])
    az_id = az.replace(region, region.replace("-", ""))  # 简化 AZ ID
    state = random.choice(["pending", "available"])
    assign_ipv6 = random.choice([True, False])
    subnets.append({
        "id": subnet_id,
        "region": region,
        "ownerid": f"{random.randint(100000000000, 999999999999)}",
        "cidr_block": cidr_block,
        "available_ip_address_count": available_ip_count,
        "default_for_az": default_for_az,
        "map_customer_owned_ip_on_launch": map_customer_owned,
        "map_public_ip_on_launch": map_public,
        "availability_zone": az,
        "availability_zone_id": az_id,
        "state": state,
        "assignipv6addressoncreation": assign_ipv6
    })

subnets_csv = os.path.join(OUTPUT_DIR, "ec2_subnets.csv")
with open(subnets_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = list(subnets[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in subnets:
        writer.writerow(row)

# 3. ec2_instances.csv
instances = []
for i in range(NUM_INSTANCES):
    instance_id = f"i-{uuid.uuid4().hex[:16]}"
    imageid = f"ami-{uuid.uuid4().hex[:8]}"
    instancetype = random.choice(["t2.micro", "c4.large", "r4.large", "m5.large"])
    iami = f"arn:aws:iam::{subnets[0]['ownerid']}:instance-profile/{uuid.uuid4().hex[:8]}"
    launchtime = f"2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z"
    launchtimeunix = random.randint(1600000000, 1700000000)
    monitoringstate = random.choice(["enabled", "disabled", "pending", "disabling"])
    state = random.choice(["running", "stopped", "terminated"])
    az = random.choice(AVAILABILITY_ZONES[subnets[0]["region"]])
    tenancy = random.choice(["default", "dedicated", "host"])
    architecture = random.choice(["x86_64", "arm64"])
    ebsoptimized = random.choice([True, False])
    bootmode = random.choice(["legacy-bios", "uefi"])
    lifecycle = random.choice(["", "spot", "scheduled"])
    hibernation = random.choice([True, False])
    instances.append({
        "id": instance_id,
        "imageid": imageid,
        "instancetype": instancetype,
        "iaminstanceprofile": iami,
        "launchtime": launchtime,
        "launchtimeunix": launchtimeunix,
        "monitoringstate": monitoringstate,
        "state": state,
        "availabilityzone": az,
        "tenancy": tenancy,
        "architecture": architecture,
        "ebsoptimized": ebsoptimized,
        "bootmode": bootmode,
        "instancelifecycle": lifecycle,
        "hibernationoptions": hibernation
    })

instances_csv = os.path.join(OUTPUT_DIR, "ec2_instances.csv")
with open(instances_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = list(instances[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in instances:
        writer.writerow(row)

# 4. network_interfaces.csv 和 ec2_instance_interfaces.csv
interfaces = []
instance_interfaces = []
for inst in instances:
    num_ifaces = random.randint(MIN_INTERFACES_PER_INSTANCE, MAX_INTERFACES_PER_INSTANCE)
    for j in range(num_ifaces):
        eni_id = f"eni-{uuid.uuid4().hex[:16]}"
        mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
        description = f"Interface {j+1} for {inst['id']}"
        private_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        private_dns = f"ip-{private_ip.replace('.', '-')}.ec2.internal"
        public_ip = f"{random.randint(52,54)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        status = random.choice(["available", "associated", "attaching", "in-use", "detaching"])
        subnet = random.choice(subnets)
        interface_type = random.choice(["interface", "efa"])
        source_dest = random.choice([True, False])
        interfaces.append({
            "id": eni_id,
            "mac_address": mac,
            "description": description,
            "private_ip_address": private_ip,
            "private_dns_name": private_dns,
            "public_ip": public_ip,
            "status": status,
            "subnetid": subnet["id"],
            "interface_type": interface_type,
            "source_dest_check": source_dest
        })
        instance_interfaces.append({
            "instance_id": inst["id"],
            "interface_id": eni_id
        })

interfaces_csv = os.path.join(OUTPUT_DIR, "network_interfaces.csv")
with open(interfaces_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = list(interfaces[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in interfaces:
        writer.writerow(row)

instance_interfaces_csv = os.path.join(OUTPUT_DIR, "ec2_instance_interfaces.csv")
with open(instance_interfaces_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["instance_id", "interface_id"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in instance_interfaces:
        writer.writerow(row)

# 5. aws_inspector_findings.csv
findings = []

# First, ensure CVE-2021-44228 (Log4j) has at least 20 findings
log4j_cve = "CVE-2021-44228"
log4j_findings_needed = 20
log4j_instances = random.sample(instances, min(log4j_findings_needed, len(instances)))

for i, inst in enumerate(log4j_instances):
    finding_arn = f"arn:aws:inspector:{subnets[0]['region']}:{subnets[0]['ownerid']}:finding/{uuid.uuid4().hex}"
    title = f"Apache Log4j Remote Code Execution Vulnerability - {inst['id']}"
    status = random.choice(["ACTIVE", "RESOLVED"])
    severity = "CRITICAL"  # Log4j is always critical
    first_obs = f"2025-{random.randint(1,6):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z"
    last_obs = first_obs
    description = f"Apache Log4j vulnerability CVE-2021-44228 detected on instance {inst['id']}. This vulnerability allows remote code execution via JNDI injection in log messages."
    finding_type = "PACKAGE_VULNERABILITY"
    inspector_score = round(random.uniform(95, 100), 2)  # High inspector score for Log4j
    cvss_score = 10.0  # Log4j has CVSS score of 10.0
    findings.append({
        "id": finding_arn,
        "region": subnets[0]["region"],
        "title": title,
        "instance_id": inst["id"],
        "status": status,
        "severity": severity,
        "first_observed_at": first_obs,
        "last_observed_at": last_obs,
        "description": description,
        "finding_type": finding_type,
        "inspector_score": inspector_score,
        "cvss_score": cvss_score,
        "vulnerability_id": log4j_cve
    })

# Track instances that already have Log4j findings to avoid duplicates
instances_with_log4j = {inst["id"] for inst in log4j_instances}

# Then generate regular findings for all instances
for inst in instances:
    num_findings = random.randint(MIN_FINDINGS_PER_INSTANCE, MAX_FINDINGS_PER_INSTANCE)
    for k in range(num_findings):
        finding_arn = f"arn:aws:inspector:{subnets[0]['region']}:{subnets[0]['ownerid']}:finding/{uuid.uuid4().hex}"
        title = f"Finding {k+1} for {inst['id']}"
        status = random.choice(["ACTIVE", "RESOLVED"])
        severity = random.choice(["LOW", "MEDIUM", "HIGH", "CRITICAL"])
        first_obs = f"2025-{random.randint(1,6):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z"
        last_obs = first_obs
        description = f"Description for {finding_arn}"
        finding_type = random.choice(["NETWORK_REACHABILITY", "PACKAGE_VULNERABILITY"])
        inspector_score = round(random.uniform(0, 100), 2)
        cvss_score = round(random.uniform(0, 10), 1) if finding_type == "PACKAGE_VULNERABILITY" else ""
        
        # Select vulnerability ID, but avoid Log4j for instances that already have it
        if finding_type == "PACKAGE_VULNERABILITY":
            if inst["id"] in instances_with_log4j:
                # For instances with Log4j, select other CVEs
                other_cves = [cve for cve in cve_data if cve["id"] != log4j_cve]
                if other_cves:
                    vulnerability_id = random.choices(
                        [cve["id"] for cve in other_cves],
                        weights=[cve["weight"] for cve in other_cves]
                    )[0]
                else:
                    vulnerability_id = "CVE-2021-0001"  # Fallback
            else:
                vulnerability_id = select_weighted_cve()
        else:
            vulnerability_id = ""
            
        findings.append({
            "id": finding_arn,
            "region": subnets[0]["region"],
            "title": title,
            "instance_id": inst["id"],
            "status": status,
            "severity": severity,
            "first_observed_at": first_obs,
            "last_observed_at": last_obs,
            "description": description,
            "finding_type": finding_type,
            "inspector_score": inspector_score,
            "cvss_score": cvss_score,
            "vulnerability_id": vulnerability_id
        })

findings_csv = os.path.join(OUTPUT_DIR, "aws_inspector_findings.csv")
with open(findings_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = list(findings[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in findings:
        writer.writerow(row)

# 6. Categorize instances as external-facing or internal
external_facing_instances = random.sample(instances, int(len(instances) * EXTERNAL_FACING_RATIO))
external_facing_instance_ids = {inst["id"] for inst in external_facing_instances}

# Get interfaces for external-facing instances
external_facing_interfaces = [
    iface for iface in interfaces 
    if any(ii["instance_id"] in external_facing_instance_ids 
           for ii in instance_interfaces if ii["interface_id"] == iface["id"])
]

# 7. external_ip_addresses.csv
external_ips = []
known_malicious_ips = []
threat_categories = ["botnet", "scanner", "malware_c2", "phishing", "tor_exit", "suspicious"]
countries = ["US", "CN", "RU", "DE", "BR", "IN", "GB", "FR", "CA", "JP"]
as_orgs = ["Amazon.com", "Google", "Microsoft", "Cloudflare", "Akamai", "Digital Ocean", "Linode", "Hetzner"]

for i in range(NUM_EXTERNAL_IPS):
    # Generate realistic external IP (avoiding private ranges)
    while True:
        ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
        ip_obj = ipaddress.IPv4Address(ip)
        if not ip_obj.is_private and not ip_obj.is_loopback and not ip_obj.is_multicast:
            break
    
    is_malicious = random.random() < 0.1  # 10% chance of being malicious
    if is_malicious:
        known_malicious_ips.append(ip)
    
    external_ips.append({
        "ip_address": ip,
        "ip_type": "public",
        "geolocation_country": random.choice(countries),
        "geolocation_region": f"Region-{random.randint(1,10)}",
        "geolocation_city": f"City-{random.randint(1,100)}",
        "asn": random.randint(1000, 70000),
        "as_org": random.choice(as_orgs),
        "is_known_malicious": is_malicious,
        "threat_category": random.choice(threat_categories) if is_malicious else "",
        "first_seen": f"2025-{random.randint(1,6):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
        "last_seen": f"2025-{random.randint(1,6):02d}-{random.randint(1,28):02d}T{random.randint(0,23):02d}:{random.randint(0,59):02d}:00Z",
        "reputation_score": random.randint(10, 30) if is_malicious else random.randint(70, 100)
    })

external_ips_csv = os.path.join(OUTPUT_DIR, "external_ip_addresses.csv")
with open(external_ips_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = list(external_ips[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in external_ips:
        writer.writerow(row)

# 8. vpc_flow_to_external.csv
vpc_flows_external = []
protocols = {6: "TCP", 17: "UDP", 1: "ICMP"}
common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306]

for i in range(NUM_EXTERNAL_FLOWS):
    flow_id = f"flow-ext-{uuid.uuid4().hex[:16]}"
    src_interface = random.choice(external_facing_interfaces)  # Only external-facing interfaces
    dst_ip = random.choice(external_ips)["ip_address"]
    
    protocol_num = random.choice(list(protocols.keys()))
    srcport = random.randint(32768, 65535) if protocol_num in [6, 17] else 0
    dstport = random.choice(common_ports) if protocol_num in [6, 17] else 0
    
    # Bias towards ACCEPT for legitimate traffic, more REJECT for malicious IPs
    if dst_ip in known_malicious_ips:
        action = random.choices(["ACCEPT", "REJECT"], weights=[30, 70])[0]
    else:
        action = random.choices(["ACCEPT", "REJECT"], weights=[85, 15])[0]
    
    window_start = random.randint(1704067200, 1709251200)  # Jan-Mar 2025
    window_end = window_start + random.randint(60, 3600)  # 1 min to 1 hour duration
    
    vpc_flows_external.append({
        "id": flow_id,
        "from_interface_id": src_interface["id"],
        "to_external_ip": dst_ip,
        "srcport": srcport,
        "dstport": dstport,
        "protocol": protocol_num,
        "packets": random.randint(1, 1000),
        "bytes": random.randint(64, 65536),
        "windowstart": window_start,
        "windowend": window_end,
        "action": action,
        "flowlogstatus": random.choice(["OK", "NODATA", "SKIPDATA"]),
        "flow_direction": random.choice(["ingress", "egress"]),
        "region": random.choice(REGIONS),
        "account_id": f"{random.randint(100000000000, 999999999999)}",
        "tcp_flags": random.randint(0, 255) if protocol_num == 6 else 0,
        "traffic_path": random.randint(1, 8)
    })

vpc_flows_external_csv = os.path.join(OUTPUT_DIR, "vpc_flow_to_external.csv")
with open(vpc_flows_external_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = list(vpc_flows_external[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in vpc_flows_external:
        writer.writerow(row)

# 9. vpc_flow_between_interfaces.csv
vpc_flows_internal = []

for i in range(NUM_INTERNAL_FLOWS):
    flow_id = f"flow-int-{uuid.uuid4().hex[:16]}"
    src_interface = random.choice(interfaces)
    
    # Find a different interface, preferably in same subnet for realism
    same_subnet_interfaces = [iface for iface in interfaces 
                            if iface["subnetid"] == src_interface["subnetid"] 
                            and iface["id"] != src_interface["id"]]
    
    if same_subnet_interfaces and random.random() < 0.7:  # 70% chance same subnet
        dst_interface = random.choice(same_subnet_interfaces)
    else:
        dst_interface = random.choice([iface for iface in interfaces if iface["id"] != src_interface["id"]])
    
    protocol_num = random.choice(list(protocols.keys()))
    srcport = random.randint(32768, 65535) if protocol_num in [6, 17] else 0
    dstport = random.choice(common_ports) if protocol_num in [6, 17] else 0
    
    # Internal traffic is mostly accepted
    action = random.choices(["ACCEPT", "REJECT"], weights=[90, 10])[0]
    
    window_start = random.randint(1704067200, 1709251200)  # Jan-Mar 2025
    window_end = window_start + random.randint(60, 3600)  # 1 min to 1 hour duration
    
    vpc_flows_internal.append({
        "id": flow_id,
        "from_interface_id": src_interface["id"],
        "to_interface_id": dst_interface["id"],
        "srcport": srcport,
        "dstport": dstport,
        "protocol": protocol_num,
        "packets": random.randint(1, 500),
        "bytes": random.randint(64, 32768),
        "windowstart": window_start,
        "windowend": window_end,
        "action": action,
        "flowlogstatus": random.choice(["OK", "NODATA", "SKIPDATA"]),
        "flow_direction": random.choice(["ingress", "egress"]),
        "region": random.choice(REGIONS),
        "account_id": f"{random.randint(100000000000, 999999999999)}",
        "tcp_flags": random.randint(0, 255) if protocol_num == 6 else 0,
        "traffic_path": random.randint(1, 8)
    })

vpc_flows_internal_csv = os.path.join(OUTPUT_DIR, "vpc_flow_between_interfaces.csv")
with open(vpc_flows_internal_csv, "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = list(vpc_flows_internal[0].keys())
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in vpc_flows_internal:
        writer.writerow(row)

print("CSV files generated in directory:", OUTPUT_DIR)
print("- ec2_subnets.csv")
print("- ec2_instances.csv")
print("- network_interfaces.csv")
print("- ec2_instance_interfaces.csv")
print("- aws_inspector_findings.csv")
print("- external_ip_addresses.csv")
print("- vpc_flow_to_external.csv")
print("- vpc_flow_between_interfaces.csv")
print(f"Generated {len(external_facing_instances)} external-facing instances out of {len(instances)} total")
print(f"Generated {len(external_ips)} external IP addresses ({len(known_malicious_ips)} marked as malicious)")
print(f"Generated {len(vpc_flows_external)} external flows and {len(vpc_flows_internal)} internal flows")
print(f"Generated {len(log4j_instances)} CVE-2021-44228 (Log4j) findings out of {len(findings)} total findings")
