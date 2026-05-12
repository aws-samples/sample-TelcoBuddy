"""Stack 2: Open5GS 5G Core — 13 NFs on EKS from ECR Public images."""
import aws_cdk as cdk
from aws_cdk import aws_eks as eks
from constructs import Construct
from config import get_image_uri


# NF definitions: name, binary, port, protocol
NFS = [
    ("nrf",  "nrfd",  7777,  "TCP"),
    ("scp",  "scpd",  7777,  "TCP"),
    ("amf",  "amfd",  38412, "SCTP"),
    ("smf",  "smfd",  8805,  "TCP"),
    ("upf",  "upfd",  8805,  "TCP"),
    ("ausf", "ausfd", 7777,  "TCP"),
    ("udm",  "udmd",  7777,  "TCP"),
    ("udr",  "udrd",  7777,  "TCP"),
    ("pcf",  "pcfd",  7777,  "TCP"),
    ("nssf", "nssfd", 7777,  "TCP"),
    ("bsf",  "bsfd",  7777,  "TCP"),
]


class Open5gsStack(cdk.Stack):
    def __init__(self, scope: Construct, id: str, cluster: eks.ICluster,
                 config: dict, nf_ns_manifest, **kwargs):
        super().__init__(scope, id, **kwargs)

        ns = config["nf_namespace"]
        ecr_alias = config["ecr_public_alias"]
        open5gs_image = get_image_uri(ecr_alias, "open5gs", config["open5gs_tag"])
        mongo_image = get_image_uri(ecr_alias, "mongo", config["mongo_tag"])
        webui_image = get_image_uri(ecr_alias, "webui", config["open5gs_tag"])

        # MongoDB — must deploy first
        mongo_deploy = cluster.add_manifest("MongoDb", {
            "apiVersion": "apps/v1", "kind": "Deployment",
            "metadata": {"name": "mongodb", "namespace": ns},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "mongodb"}},
                "template": {
                    "metadata": {"labels": {"app": "mongodb"}},
                    "spec": {"containers": [{
                        "name": "mongodb", "image": mongo_image,
                        "ports": [{"containerPort": 27017}],
                    }]},
                },
            },
        })
        mongo_deploy.node.add_dependency(nf_ns_manifest)

        mongo_svc = cluster.add_manifest("MongoDbSvc", {
            "apiVersion": "v1", "kind": "Service",
            "metadata": {"name": "mongodb", "namespace": ns},
            "spec": {
                "selector": {"app": "mongodb"},
                "ports": [{"port": 27017, "targetPort": 27017}],
            },
        })
        mongo_svc.node.add_dependency(mongo_deploy)

        # Mongo alias (some NFs reference 'mongo' not 'mongodb')
        cluster.add_manifest("MongoAlias", {
            "apiVersion": "v1", "kind": "Service",
            "metadata": {"name": "mongo", "namespace": ns},
            "spec": {"type": "ExternalName", "externalName": f"mongodb.{ns}.svc.cluster.local"},
        }).node.add_dependency(mongo_svc)

        # NFs that require MongoDB connection
        MONGO_NFS = {"udr", "pcf", "bsf"}

        # 11 Open5GS NFs
        prev = mongo_svc
        for nf_name, binary, port, proto in NFS:
            container = {
                "name": nf_name, "image": open5gs_image,
                "command": [f"/opt/open5gs/bin/open5gs-{binary}"],
                "ports": [{"containerPort": port, "protocol": proto}],
            }
            if nf_name in MONGO_NFS:
                container["env"] = [{"name": "DB_URI", "value": f"mongodb://mongodb.{ns}.svc.cluster.local/open5gs"}]
            if nf_name == "upf":
                container["securityContext"] = {"capabilities": {"add": ["NET_ADMIN"]}, "privileged": True}

            deploy = cluster.add_manifest(f"Nf{nf_name.capitalize()}Deploy", {
                "apiVersion": "apps/v1", "kind": "Deployment",
                "metadata": {"name": nf_name, "namespace": ns,
                             "labels": {"app": nf_name, "nf": nf_name}},
                "spec": {
                    "replicas": 1,
                    "selector": {"matchLabels": {"app": nf_name}},
                    "template": {
                        "metadata": {"labels": {"app": nf_name, "nf": nf_name}},
                        "spec": {"containers": [container]},
                    },
                },
            })
            deploy.node.add_dependency(prev if nf_name == "nrf" else nf_ns_manifest)

            svc = cluster.add_manifest(f"Nf{nf_name.capitalize()}Svc", {
                "apiVersion": "v1", "kind": "Service",
                "metadata": {"name": nf_name, "namespace": ns},
                "spec": {
                    "selector": {"app": nf_name},
                    "ports": [{"port": port, "targetPort": port,
                               "protocol": proto}],
                },
            })
            svc.node.add_dependency(deploy)

            # NRF must be up before other NFs register
            if nf_name == "nrf":
                prev = svc

        # WebUI
        webui_deploy = cluster.add_manifest("WebuiDeploy", {
            "apiVersion": "apps/v1", "kind": "Deployment",
            "metadata": {"name": "webui", "namespace": ns},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "webui"}},
                "template": {
                    "metadata": {"labels": {"app": "webui"}},
                    "spec": {"containers": [{
                        "name": "webui", "image": webui_image,
                        "ports": [{"containerPort": 9999}],
                    }]},
                },
            },
        })
        webui_deploy.node.add_dependency(mongo_svc)

        cluster.add_manifest("WebuiSvc", {
            "apiVersion": "v1", "kind": "Service",
            "metadata": {"name": "webui", "namespace": ns},
            "spec": {
                "selector": {"app": "webui"},
                "ports": [{"port": 9999, "targetPort": 9999}],
            },
        }).node.add_dependency(webui_deploy)
