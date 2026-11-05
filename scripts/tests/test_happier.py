import pathlib, unittest, yaml
B = pathlib.Path(__file__).resolve().parents[2] / 'kubernetes/apps/ai/happier'
class Baseline(unittest.TestCase):
 def test_database(self):
  p=B/'database/database.yaml'
  self.assertTrue(p.exists(), 'dedicated Happier PostgreSQL missing')
  d=yaml.safe_load(p.read_text())
  self.assertEqual(d['spec'], dict(name='happier', owner='happier', cluster=dict(name='postgres'), databaseReclaimPolicy='retain'))
 def test_dns(self):
  p=B/'app/dnsendpoint.yaml'
  self.assertTrue(p.exists(), 'private Happier DNS missing')
  d=yaml.safe_load(p.read_text())
  self.assertEqual(d['metadata']['labels']['dns.homelab/external'], 'false')
  self.assertEqual(d['spec']['endpoints'][0]['targets'], ['internal.${DOMAIN_5}'])
if __name__=='__main__': unittest.main()
