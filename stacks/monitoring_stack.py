"""Stack 1c: Prometheus + Grafana via Helm, custom PrometheusRule, AlertManager placeholder."""
import aws_cdk as cdk
from aws_cdk import aws_eks as eks
from constructs import Construct
import json


class MonitoringStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, cluster: eks.ICluster,
                 config: dict, monitoring_ns_manifest, **kwargs):
        super().__init__(scope, id, **kwargs)

        pn = config["project_name"]
        ns = config["nf_namespace"]
        scrape = config.get("prometheus_scrape_interval", "5s")

        # Helm: kube-prometheus-stack
        prometheus = cluster.add_helm_chart("Prometheus",
            chart="kube-prometheus-stack",
            repository="https://prometheus-community.github.io/helm-charts",
            namespace="monitoring",
            release="prometheus",
            values={
                "prometheus": {"prometheusSpec": {"serviceMonitorSelectorNilUsesHelmValues": False,
                    "ruleSelectorNilUsesHelmValues": False}},
                "alertmanager": {"enabled": True},
                "grafana": {"enabled": True},
                "kubeStateMetrics": {"serviceMonitor": {
                    "interval": scrape,
                    "scrapeTimeout": "4s",
                    "honorLabels": True,
                }},
            },
        )
        prometheus.node.add_dependency(monitoring_ns_manifest)

        # Custom PrometheusRule — 9 alerts for 5G NFs
        prom_rule = cluster.add_manifest("NfAlerts", {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "PrometheusRule",
            "metadata": {"name": f"{pn}-nf-alerts", "namespace": "monitoring",
                         "labels": {"release": "prometheus", "team": pn}},
            "spec": {"groups": [
                {"name": f"{pn}-infra", "rules": [
                    {"alert": "NFScaledToZero",
                     "expr": f'kube_deployment_spec_replicas{{namespace="{ns}"}} == 0',
                     "for": "0s",
                     "labels": {"severity": "critical", "category": "INFRA", "team": pn},
                     "annotations": {"summary": "{{ $labels.deployment }} scaled to zero",
                                     "impact": "Complete NF outage"}},
                    {"alert": "NFCrashLooping",
                     "expr": f'rate(kube_pod_container_status_restarts_total{{namespace="{ns}"}}[5m]) > 0',
                     "for": "0s",
                     "labels": {"severity": "critical", "category": "INFRA", "team": pn},
                     "annotations": {"summary": "{{ $labels.pod }} crash looping",
                                     "impact": "Intermittent NF availability"}},
                    {"alert": "NFOOMKilled",
                     "expr": f'kube_pod_container_status_last_terminated_reason{{namespace="{ns}",reason="OOMKilled"}} == 1',
                     "for": "0s",
                     "labels": {"severity": "critical", "category": "INFRA", "team": pn},
                     "annotations": {"summary": "{{ $labels.pod }} OOM killed",
                                     "impact": "NF memory exhaustion"}},
                ]},
                {"name": f"{pn}-degradation", "rules": [
                    {"alert": "NFHighCPU",
                     "expr": f'rate(container_cpu_usage_seconds_total{{namespace="{ns}",container!=""}}[2m]) * 100 > 80',
                     "for": "30s",
                     "labels": {"severity": "warning", "category": "PERF", "team": pn},
                     "annotations": {"summary": "{{ $labels.pod }} CPU > 80%",
                                     "impact": "NF performance degradation"}},
                    {"alert": "NFHighMemory",
                     "expr": f'container_memory_working_set_bytes{{namespace="{ns}",container!=""}} / container_spec_memory_limit_bytes{{namespace="{ns}",container!=""}} * 100 > 85',
                     "for": "30s",
                     "labels": {"severity": "warning", "category": "PERF", "team": pn},
                     "annotations": {"summary": "{{ $labels.pod }} memory > 85%",
                                     "impact": "Risk of OOM kill"}},
                    {"alert": "NFHighLatency",
                     "expr": f'rate(container_cpu_cfs_throttled_seconds_total{{namespace="{ns}",container!=""}}[2m]) > 0.5',
                     "for": "30s",
                     "labels": {"severity": "warning", "category": "PERF", "team": pn},
                     "annotations": {"summary": "{{ $labels.pod }} CPU throttled",
                                     "impact": "N1/N2/N4 message processing delays"}},
                    {"alert": "NFNotReady",
                     "expr": f'kube_deployment_status_replicas_unavailable{{namespace="{ns}"}} > 0',
                     "for": "30s",
                     "labels": {"severity": "warning", "category": "INFRA", "team": pn},
                     "annotations": {"summary": "{{ $labels.deployment }} has unavailable replicas",
                                     "impact": "Reduced NF capacity"}},
                    {"alert": "NFPersistentVolumeIssue",
                     "expr": f'kube_persistentvolumeclaim_status_phase{{namespace="{ns}"}} != 1',
                     "for": "60s",
                     "labels": {"severity": "warning", "category": "STORAGE", "team": pn},
                     "annotations": {"summary": "PVC issue in {{ $labels.namespace }}",
                                     "impact": "MongoDB/UDR data persistence at risk"}},
                    {"alert": "NFNetworkErrors",
                     "expr": f'rate(container_network_receive_errors_total{{namespace="{ns}"}}[5m]) + rate(container_network_transmit_errors_total{{namespace="{ns}"}}[5m]) > 0',
                     "for": "30s",
                     "labels": {"severity": "warning", "category": "NETWORK", "team": pn},
                     "annotations": {"summary": "Network errors in {{ $labels.pod }}",
                                     "impact": "Inter-NF communication degraded"}},
                ]},
            ]},
        })
        prom_rule.node.add_dependency(prometheus)
