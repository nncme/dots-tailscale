"""No-network/no-key regression checks for the owner fork's fixed SSH port."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SETUP = (ROOT / 'tailscale-setup.sh').read_text()


class ForkSSHPortTests(unittest.TestCase):
    def preflight(self, threshold):
        function = re.search(r'^preflight\(\) \{\n.*?^}\n', SETUP, re.M | re.S).group()
        script = ('D=/fixture\n'
                  'fail() { echo "$*" >&2; exit 1; }\n'
                  'require() { :; }\n'
                  'uname() { if [[ "$1" = -s ]]; then echo Linux; else echo x86_64; fi; }\n'
                  'cat() { echo ' + str(threshold) + '; }\n' + function + '\npreflight\n')
        return subprocess.run(['bash', '-c', script], capture_output=True, text=True, timeout=5)

    def test_regular_unprivileged_threshold_allowed(self):
        self.assertEqual(self.preflight(1024).returncode, 0)
        self.assertEqual(self.preflight(2222).returncode, 0)

    def test_threshold_above_selected_port_refused(self):
        result = self.preflight(2223)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unprivileged port 2222 unavailable', result.stderr)

    def test_generated_config_and_startup_probe_agree(self):
        self.assertIn('Port 2222\nListenAddress 127.0.0.1\n', SETUP)
        self.assertIn("socket.create_connection(('127.0.0.1',2222)", SETUP)
        self.assertNotIn('Port 22\n', SETUP)

    def test_update_listener_and_readiness_agree(self):
        helper = (ROOT / 'dots-ts').read_text()
        self.assertIn("('sshd', 2222)", helper)
        self.assertIn("socket.create_connection(('127.0.0.1', 2222)", helper)
        self.assertNotIn("('sshd', 22)", helper)


if __name__ == '__main__':
    unittest.main()
