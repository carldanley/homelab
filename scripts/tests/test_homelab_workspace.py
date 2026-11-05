"""Source-only selector contract; no sibling checkout or YAML dependency."""
from pathlib import Path
import unittest
import re

ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTICS = ROOT / 'kubernetes/apps/coder-workspaces/workspaces/app/homelab-diagnostics.yaml'


class HomelabDiagnosticAccess(unittest.TestCase):
    def test_curated_cluster_reader_contract(self):
        text = DIAGNOSTICS.read_text()
        role, binding = text.strip().lstrip('-\n').split('\n---\n')
        self.assertIn('\nkind: ClusterRole\n', role)
        self.assertIn('\nkind: ClusterRoleBinding\n', binding)
        self.assertNotIn('namespace:', role)
        self.assertEqual(binding.split('roleRef:\n')[1],
                         '  apiGroup: rbac.authorization.k8s.io\n'
                         '  kind: ClusterRole\n'
                         '  name: homelab-workspace-reader\n'
                         'subjects:\n'
                         '  - kind: ServiceAccount\n'
                         '    name: homelab-workspace\n'
                         '    namespace: homelab-workspaces')
        self.assertIn('  name: homelab-workspace-reader\n', role)
        self.assertIn('  name: homelab-workspace-reader\n', binding)
        expected = {
            '': 'namespaces nodes pods services endpoints persistentvolumeclaims persistentvolumes events',
            'apps': 'deployments replicasets statefulsets daemonsets controllerrevisions',
            'batch': 'jobs cronjobs',
            'networking.k8s.io': 'ingresses ingressclasses networkpolicies',
            'discovery.k8s.io': 'endpointslices',
            'storage.k8s.io': 'storageclasses volumeattachments csidrivers csinodes csistoragecapacities',
            'policy': 'poddisruptionbudgets',
            'autoscaling': 'horizontalpodautoscalers',
            'events.k8s.io': 'events',
            'metrics.k8s.io': 'pods nodes',
            'source.toolkit.fluxcd.io': 'gitrepositories ocirepositories helmrepositories helmcharts buckets',
            'kustomize.toolkit.fluxcd.io': 'kustomizations',
            'helm.toolkit.fluxcd.io': 'helmreleases',
            'cilium.io': 'ciliumnetworkpolicies ciliumclusterwidenetworkpolicies',
        }
        allowed = {(group, resource, ('get', 'list') if group == 'metrics.k8s.io' else ('get', 'list', 'watch'))
                   for group, resources in expected.items() for resource in resources.split()}
        allowed.add(('', 'pods/log', ('get',)))
        rules = role.split('rules:\n', 1)[1]
        pattern = r'  - apiGroups: \[([^\]]*)\]\n    resources: \[([^\]]+)\]\n    verbs: \[([^\]]+)\]\n?'
        matches = list(re.finditer(pattern, rules))
        self.assertEqual(''.join(match.group(0) for match in matches), rules)
        actual = set()
        for match in matches:
            group, resources, verbs = match.groups()
            group = group.strip().strip('"')
            verbs = tuple(item.strip() for item in verbs.split(','))
            for resource in resources.split(','):
                actual.add((group, resource.strip(), verbs))
        self.assertEqual(actual, allowed)
        # Exact tuple equality rejects wildcards, extra API groups/resources,
        # writes, RBAC/Secret/ConfigMap reads and privileged subresources.
        self.assertNotIn('nonResourceURLs', text)


POLICY = Path(__file__).resolve().parents[2] / "kubernetes/apps/homelab-workspaces/workspaces/app/ciliumnetworkpolicy.yaml"


class HomelabWorkspaceSelectors(unittest.TestCase):
    def test_endpoint_selectors_match_workspace_pods(self):
        # Scope to endpoint selectors, excluding egress destination labels.
        blocks = POLICY.read_text().split("  endpointSelector:\n")[1:]
        self.assertEqual(len(blocks), 2)
        for block in blocks:
            selector = block.split("  egress:", 1)[0]
            with self.subTest(selector=selector):
                self.assertNotIn("coder-workspace", selector)
                self.assertEqual(selector.strip(), "matchLabels:\n      app.kubernetes.io/name: homelab-workspace")
