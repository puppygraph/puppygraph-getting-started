# CSPM on ClickHouse with PuppyGraph

A Cloud Security Posture Management (CSPM) demo that models AWS-style
network and IAM relationships in ClickHouse and exposes them as a graph
through PuppyGraph. The showcase query traces the path from
internet-exposed VMs through role-assumption chains to sensitive data
resources — the kind of multi-hop reachability question that is awkward
in SQL and natural in graph.

## Files

- `docker-compose.yaml` — PuppyGraph + ClickHouse services
- `schema.json` — graph schema (table → vertex/edge mapping)
- `load.sh` — creates the `cspm` database, DDL, and loads CSVs
- `drop.sh` — drops the `cspm` database (re-run `load.sh` to rebuild)
- `csv_data/` — seeded dataset

## The data

The seeded dataset in `csv_data/` is loaded into 15 ClickHouse tables
in the `cspm` database. The tables fall into two groups:

**Entity tables** :

| Table               | Rows | Notes                                       |
|---------------------|-----:|---------------------------------------------|
| `Users`             |  200 | with `account_status`, `auth_method`, etc.  |
| `VPCs`              |    4 | prod-payments, prod-platform, staging-billing, dev-sandbox |
| `InternetGateways`  |    4 | one per VPC                                 |
| `Subnets`           |   16 | 4 per VPC (2 public + 2 private)            |
| `SecurityGroups`    |   24 | 6 per VPC (web, app, db, mgmt, monitoring, internal) |
| `IngressRules`      |   32 | some open `0.0.0.0/0` (deliberately risky)  |
| `NetworkInterfaces` |  200 | one per VM                                  |
| `VMInstances`       |  200 | each assigned a `Role`                      |
| `PublicIPs`         |   15 | only on internet-facing NIs                 |
| `Roles`             |   14 | per business unit × privilege tier          |
| `Resources`         |   48 | with sensitivity = pii / secret / internal / public |

**Relationship tables**:

| Table                          | Becomes edge                                        |
|--------------------------------|-----------------------------------------------------|
| `InternetGatewayVPC`           | `(InternetGateway)-[:GATEWAY_TO]->(VPC)`            |
| `RoleResourceAccess`           | `(Role)-[:ALLOWS_ACCESS_TO]->(Resource)`            |
| `RoleAssumeRole`               | `(Role)-[:CAN_ASSUME]->(Role)`                      |
| `UserRoleAssumption`           | `(User)-[:CAN_ASSUME_ROLE]->(Role)`                 |

## The graph model

`schema.json` defines 11 vertex types and 11 edge types over the
ClickHouse tables.

**Vertices** — label, source table, and attributes (the first column
of each row is the vertex `id`):

| Label              | Source table        | Attributes                                                                                                                  |
|--------------------|---------------------|-----------------------------------------------------------------------------------------------------------------------------|
| `User`             | `Users`             | `user_id`, `username`, `email`, `phone`, `created_at`, `last_login`, `account_status`, `authentication_method`, `failed_login_attempts` |
| `InternetGateway`  | `InternetGateways`  | `internet_gateway_id`, `name`, `region`, `status`                                                                           |
| `VPC`              | `VPCs`              | `vpc_id`, `name`                                                                                                            |
| `Subnet`           | `Subnets`           | `subnet_id`, `name`                                                                                                         |
| `SecurityGroup`    | `SecurityGroups`    | `security_group_id`, `name`                                                                                                 |
| `NetworkInterface` | `NetworkInterfaces` | `network_interface_id`, `name`                                                                                              |
| `VMInstance`       | `VMInstances`       | `vm_instance_id`, `name`                                                                                                    |
| `Role`             | `Roles`             | `role_id`, `name`                                                                                                           |
| `Resource`         | `Resources`         | `resource_id`, `name`, `type`, `sensitivity`                                                                                |
| `PublicIP`         | `PublicIPs`         | `public_ip_id`, `ip_address`                                                                                                |
| `IngressRule`      | `IngressRules`      | `ingress_rule_id`, `protocol`, `port_range`, `source`                                                                       |

**Edges** — label, endpoints, source table, and attributes:

| Edge                  | From → To                          | Source table                   | Attributes                                                  |
|-----------------------|------------------------------------|--------------------------------|-------------------------------------------------------------|
| `CAN_ASSUME_ROLE`     | `User` → `Role`                    | `UserRoleAssumption`           | `granted_at`                                                |
| `GATEWAY_TO`          | `InternetGateway` → `VPC`          | `InternetGatewayVPC`           | —                                                           |
| `CONTAINS`            | `VPC` → `Subnet`                   | `Subnets`                      | —                                                           |
| `HOSTS_INTERFACE`     | `Subnet` → `NetworkInterface`      | `NetworkInterfaces`            | —                                                           |
| `PROTECTS`            | `SecurityGroup` → `NetworkInterface` | `NetworkInterfaces`          | —                                                           |
| `HAS_RULE`            | `SecurityGroup` → `IngressRule`    | `IngressRules`                 | —                                                           |
| `HAS_PUBLIC_IP`       | `NetworkInterface` → `PublicIP`    | `PublicIPs`                    | —                                                           |
| `ATTACHED_TO`         | `NetworkInterface` → `VMInstance`  | `VMInstances`                  | —                                                           |
| `ASSIGNED_ROLE`       | `VMInstance` → `Role`              | `VMInstances`                  | —                                                           |
| `CAN_ASSUME`          | `Role` → `Role`                    | `RoleAssumeRole`               | —                                                           |
| `ALLOWS_ACCESS_TO`    | `Role` → `Resource`                | `RoleResourceAccess`           | —                                                           |

## Prerequisites

- Docker and Docker Compose

## Quick start

1. Bring up ClickHouse + PuppyGraph
  ```bash
  docker compose up -d
  ```

2. Create the schema and load the seeded CSVs into ClickHouse
  ```bash
  ./load.sh
  ```

3. Log into the PuppyGraph UI at `http://localhost:8081` with the credentials set in `docker-compose.yaml`:
   - Username: `puppygraph`
   - Password: `puppygraph123`

  Click **Graph** in the sidebar, then click **Upload Schema** and select the `schema.json` file.

Once the schema is uploaded, head to the **Query** page and try the
queries below.

## Queries

All queries are written in openCypher, while PuppyGraph also supports Gremlin.

### Publicly-exposed VMs

Find every VM that has a public IP and whose subnet sits behind an
internet gateway. Returns 15 rows on the seeded data.

```cypher
MATCH (ig:InternetGateway)-[:GATEWAY_TO]->(vpc:VPC)
      -[:CONTAINS]->(s:Subnet)
      -[:HOSTS_INTERFACE]->(ni:NetworkInterface)
      -[:HAS_PUBLIC_IP]->(pip:PublicIP),
      (ni)-[:ATTACHED_TO]->(vm:VMInstance)
RETURN vm.name        AS vm,
       pip.ip_address AS public_ip,
       vpc.name       AS vpc,
       ig.name        AS internet_gateway
ORDER BY vm
```

### Internet-exposed VMs that can reach sensitive data

A VM is flagged when **all three** conditions hold:

1. It is reachable from the internet (public IP + IGW), **and**
2. Its security group has an ingress rule open to `0.0.0.0/0` on a
   high-risk management port (22 SSH or 3389 RDP), **and**
3. The role assigned to the VM can — possibly through a chain of
   `CAN_ASSUME` hops — reach a resource of sensitivity `pii` or
   `secret`.

Returns 3 rows on the seeded data, ranked by blast radius (number of
distinct sensitive resources reachable through the role-assumption
chain).

```cypher
MATCH (ig:InternetGateway)-[:GATEWAY_TO]->(vpc:VPC)
      -[:CONTAINS]->(s:Subnet)-[:HOSTS_INTERFACE]->(ni:NetworkInterface)
      -[:HAS_PUBLIC_IP]->(pip:PublicIP),
      (ni)<-[:PROTECTS]-(sg:SecurityGroup)-[:HAS_RULE]->(rule:IngressRule),
      (ni)-[:ATTACHED_TO]->(vm:VMInstance)-[:ASSIGNED_ROLE]->(r1:Role),
      (r1)-[:CAN_ASSUME*0..3]->(r2:Role)-[:ALLOWS_ACCESS_TO]->(res:Resource)
WHERE rule.source = '0.0.0.0/0'
  AND rule.port_range IN ['22', '3389']
  AND res.sensitivity IN ['pii', 'secret']
RETURN vm.name           AS vm,
       pip.ip_address    AS public_ip,
       rule.port_range   AS open_port,
       r1.name           AS assigned_role,
       count(DISTINCT res)            AS sensitive_resources,
       collect(DISTINCT res.name)[..5] AS sample_resources
ORDER BY sensitive_resources DESC
```

The three flagged VMs sit at role-chain depths 0, 1, and 2 to
illustrate variable-length traversal:

| vm                          | open_port | assigned_role           | sensitive_resources |
|-----------------------------|-----------|-------------------------|---------------------|
| vm-staging-billing-api-001  | 22        | role-billing-readonly   | 7                   |
| vm-prod-payments-web-001    | 22        | role-payments-app       | 3                   |
| vm-prod-platform-web-001    | 3389      | role-platform-readonly  | 1                   |

### Top over-privileged users

For each user, count the distinct `pii`/`secret` resources reachable
through any chain of role assumptions of length 0–3. Returns the ten
users with the highest blast radius.

```cypher
MATCH (u:User)-[:CAN_ASSUME_ROLE]->(:Role)
      -[:CAN_ASSUME*0..3]->(:Role)
      -[:ALLOWS_ACCESS_TO]->(res:Resource)
WHERE res.sensitivity IN ['pii', 'secret']
RETURN u.username                  AS user,
       u.account_status            AS status,
       count(DISTINCT res)         AS blast_radius,
       collect(DISTINCT res.name)[..5] AS sample_resources
ORDER BY blast_radius DESC, user
LIMIT 10
```

On the seeded data this returns ten users with `blast_radius` between
14 and 10. Note that one of them has `status = locked` — a locked
account that still holds wide sensitive-data reach is itself a real
CSPM finding (the account's role assumptions weren't revoked when it
was disabled).

## Resetting the data

```bash
./drop.sh
./load.sh
```

## Tearing down

```bash
docker compose down -v
```
