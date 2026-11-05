import pathlib
import unittest
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]

class HappierDraftSafety(unittest.TestCase):
    def test_all_happier_flux_resources_are_suspended(self):
        resources = list(yaml.safe_load_all((ROOT / "kubernetes/apps/ai/happier/ks.yaml").read_text()))
        self.assertEqual(len(resources), 2)
        for resource in resources:
            self.assertEqual(resource["kind"], "Kustomization")
            self.assertIs(resource["spec"].get("suspend"), True)

    def test_password_is_only_an_external_reference(self):
        resource = yaml.safe_load((ROOT / "kubernetes/apps/ai/happier/database/externalsecret.yaml").read_text())
        self.assertEqual(resource["spec"]["target"]["template"]["data"]["password"], "{{ .password }}")
        self.assertEqual(resource["spec"]["data"][0]["remoteRef"], {"key": "happier", "property": "postgrespassword"})

    def test_suspended_happier_cannot_mutate_shared_cluster_roles(self):
        cluster = yaml.safe_load((ROOT / "kubernetes/apps/databases/cloudnative-pg/cluster/cluster.yaml").read_text())
        roles = cluster["spec"]["managed"]["roles"]
        self.assertNotIn("happier", [role["name"] for role in roles], "Suspended Happier secrets cannot satisfy an active shared CNPG role")

if __name__ == "__main__":
    unittest.main()
