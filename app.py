#!/usr/bin/env python3
"""Telco Buddy — 5G Self-Healing Platform on EKS.
Portable CDK: deploy end-to-end in any Bedrock-supported region.
"""
import aws_cdk as cdk
from stacks.network_stack import NetworkStack
from stacks.eks_stack import EksStack
from stacks.monitoring_stack import MonitoringStack

app = cdk.App()

# Config from cdk.json context
env = cdk.Environment(
    account=app.node.try_get_context("account") or None,
    region=app.node.try_get_context("region") or None,
)
pn = app.node.try_get_context("project_name") or "telco-buddy"
config = {
    "project_name": pn,
    "nf_namespace": app.node.try_get_context("nf_namespace") or "open5gs",
    "eks_version": app.node.try_get_context("eks_version") or "1.31",
    "eks_node_type": app.node.try_get_context("eks_node_type") or "t3.medium",
    "eks_node_count": int(app.node.try_get_context("eks_node_count") or 2),
    "eks_disk_size": int(app.node.try_get_context("eks_disk_size") or 20),
    "heal_mode": app.node.try_get_context("heal_mode") or "APPROVAL_REQUIRED",
    "open5gs_tag": app.node.try_get_context("open5gs_tag") or "2.6.6",
    "mongo_tag": app.node.try_get_context("mongo_tag") or "6.0",
    "ecr_public_alias": app.node.try_get_context("ecr_public_alias") or "a7y4t3f5",
    "bedrock_model": app.node.try_get_context("bedrock_model") or "auto",
    "embed_model": app.node.try_get_context("embed_model") or "amazon.titan-embed-text-v2:0",
    "prometheus_scrape_interval": app.node.try_get_context("prometheus_scrape_interval") or "5s",
    "alertmanager_group_wait": app.node.try_get_context("alertmanager_group_wait") or "2s",
    "alertmanager_group_interval": app.node.try_get_context("alertmanager_group_interval") or "2s",
    "alertmanager_repeat_interval": app.node.try_get_context("alertmanager_repeat_interval") or "5m",
}

# ═══ STEP 1: FOUNDATION ═══
network = NetworkStack(app, f"{pn}-network", config=config, env=env)

eks_stack = EksStack(app, f"{pn}-eks", vpc=network.vpc, config=config, env=env)
eks_stack.add_dependency(network)

monitoring = MonitoringStack(app, f"{pn}-monitoring",
    cluster=eks_stack.cluster, config=config,
    monitoring_ns_manifest=eks_stack.monitoring_ns, env=env)
monitoring.add_dependency(eks_stack)

# ═══ STEP 2: 5G CORE ═══
from stacks.open5gs_stack import Open5gsStack

open5gs = Open5gsStack(app, f"{pn}-open5gs",
    cluster=eks_stack.cluster, config=config,
    nf_ns_manifest=eks_stack.nf_ns, env=env)
open5gs.add_dependency(eks_stack)

# ═══ STEP 3: AI BRAIN ═══
from stacks.storage_stack import StorageStack
from stacks.ai_engine_stack import AiEngineStack
from stacks.investigation_stack import InvestigationStack

storage = StorageStack(app, f"{pn}-storage", config=config,
    cluster_name=eks_stack.cluster.cluster_name,
    k8s_admin_role_arn=eks_stack.k8s_admin_role.role_arn,
    kubectl_layer=eks_stack.kubectl_layer, env=env)
storage.add_dependency(eks_stack)

ai_engine = AiEngineStack(app, f"{pn}-ai-engine",
    issues_table=storage.issues_table, approvals_table=storage.approvals_table,
    cluster_name=eks_stack.cluster.cluster_name,
    k8s_admin_role_arn=eks_stack.k8s_admin_role.role_arn,
    nf_namespace=config["nf_namespace"],
    kubectl_layer=eks_stack.kubectl_layer,
    config=config, env=env)
ai_engine.add_dependency(storage)
ai_engine.add_dependency(eks_stack)

# Investigation stack — just a logical grouping now, tools Lambda is in ai-engine
investigation = InvestigationStack(app, f"{pn}-investigation",
    vpc=network.vpc, cluster=eks_stack.cluster,
    agent_tools_fn=ai_engine.agent_tools_fn,
    k8s_admin_role_arn=eks_stack.k8s_admin_role.role_arn,
    eks_cluster_sg=eks_stack.cluster_sg,
    config=config, env=env)
investigation.add_dependency(ai_engine)

# ═══ STEP 4: CHAOS & API & UI ═══
from stacks.chaos_lab_stack import ChaosLabStack
from stacks.api_stack import ApiStack
from stacks.ui_stack import UiStack

chaos = ChaosLabStack(app, f"{pn}-chaos-lab",
    cluster_name=eks_stack.cluster.cluster_name,
    k8s_admin_role_arn=eks_stack.k8s_admin_role.role_arn,
    agent_id=ai_engine.agent.attr_agent_id,
    agent_alias_id=ai_engine.agent_alias.attr_agent_alias_id,
    approvals_table_name=storage.approvals_table.table_name,
    kubectl_layer=eks_stack.kubectl_layer,
    config=config, env=env)
chaos.add_dependency(ai_engine)
chaos.add_dependency(eks_stack)

api = ApiStack(app, f"{pn}-api",
    agent_diagnose_fn=ai_engine.agent_diagnose_fn,
    issues_fn=storage.get_issues_fn,
    approvals_fn=storage.approvals_fn,
    chaos_fn=chaos.chaos_fn,
    cluster_name=eks_stack.cluster.cluster_name,
    k8s_admin_role_arn=eks_stack.k8s_admin_role.role_arn,
    kubectl_layer=eks_stack.kubectl_layer,
    config=config, env=env)
api.add_dependency(ai_engine)
api.add_dependency(storage)
api.add_dependency(chaos)

ui = UiStack(app, f"{pn}-ui",
    api_id=cdk.Fn.import_value(f"{pn}-api-id"),
    config=config, env=env)
ui.add_dependency(api)

# Tags
cdk.Tags.of(app).add("Project", pn)
cdk.Tags.of(app).add("auto-delete", "no")

app.synth()
