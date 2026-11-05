import subprocess, unittest
from pathlib import Path
class Contract(unittest.TestCase):
 def test_render(self):
  root=Path(__file__).resolve().parents[2]
  text=subprocess.check_output(['kustomize','build',str(root/'kubernetes/apps/coder-workspaces/workspaces/app')],text=True)
  self.assertEqual(text.count('kind: ExternalSecret'),2)
  for day in ('sunday','saturday'):
   self.assertIn('name: claude-code-account-'+day,text)
   self.assertIn('property: '+day.upper()+'_CLAUDE_CODE_OAUTH_TOKEN',text)
  self.assertEqual(text.count('secretKey: oauth-token'),2)
  self.assertEqual(text.count('key: claude-code-tokens'),2)
  self.assertNotIn('dataFrom:',text)
if __name__=='__main__': unittest.main()
