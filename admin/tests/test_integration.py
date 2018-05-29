import os
import io
import time
import pexpect
import tempfile
import subprocess

SD_DIR = ''
CURRENT_DIR = os.path.dirname(__file__)
ANSIBLE_BASE = ''

OUTPUT1 = '''app_hostname: app
app_ip: 10.20.2.2
daily_reboot_time: 5
dns_server: 8.8.8.8
enable_ssh_over_tor: true
journalist_alert_email: ''
journalist_alert_gpg_public_key: ''
journalist_gpg_fpr: ''
monitor_hostname: mon
monitor_ip: 10.20.3.2
ossec_alert_email: test@gmail.com
ossec_alert_gpg_public_key: sd_admin_test.pub
ossec_gpg_fpr: 1F544B31C845D698EB31F2FF364F1162D32E7E58
sasl_domain: gmail.com
sasl_password: testpassword
sasl_username: testuser
securedrop_app_gpg_fingerprint: 1F544B31C845D698EB31F2FF364F1162D32E7E58
securedrop_app_gpg_public_key: sd_admin_test.pub
securedrop_app_https_certificate_cert_src: ''
securedrop_app_https_certificate_chain_src: ''
securedrop_app_https_certificate_key_src: ''
securedrop_app_https_on_source_interface: false
securedrop_supported_locales:
- de_DE
- es_ES
smtp_relay: smtp.gmail.com
smtp_relay_port: 587
ssh_users: sd
'''

JOURNALIST_ALERT_OUTPUT = '''app_hostname: app
app_ip: 10.20.2.2
daily_reboot_time: 5
dns_server: 8.8.8.8
enable_ssh_over_tor: true
journalist_alert_email: test@gmail.com
journalist_alert_gpg_public_key: sd_admin_test.pub
journalist_gpg_fpr: 1F544B31C845D698EB31F2FF364F1162D32E7E58
monitor_hostname: mon
monitor_ip: 10.20.3.2
ossec_alert_email: test@gmail.com
ossec_alert_gpg_public_key: sd_admin_test.pub
ossec_gpg_fpr: 1F544B31C845D698EB31F2FF364F1162D32E7E58
sasl_domain: gmail.com
sasl_password: testpassword
sasl_username: testuser
securedrop_app_gpg_fingerprint: 1F544B31C845D698EB31F2FF364F1162D32E7E58
securedrop_app_gpg_public_key: sd_admin_test.pub
securedrop_app_https_certificate_cert_src: ''
securedrop_app_https_certificate_chain_src: ''
securedrop_app_https_certificate_key_src: ''
securedrop_app_https_on_source_interface: false
securedrop_supported_locales:
- de_DE
- es_ES
smtp_relay: smtp.gmail.com
smtp_relay_port: 587
ssh_users: sd
'''

HTTPS_OUTPUT = '''app_hostname: app
app_ip: 10.20.2.2
daily_reboot_time: 5
dns_server: 8.8.8.8
enable_ssh_over_tor: true
journalist_alert_email: test@gmail.com
journalist_alert_gpg_public_key: sd_admin_test.pub
journalist_gpg_fpr: 1F544B31C845D698EB31F2FF364F1162D32E7E58
monitor_hostname: mon
monitor_ip: 10.20.3.2
ossec_alert_email: test@gmail.com
ossec_alert_gpg_public_key: sd_admin_test.pub
ossec_gpg_fpr: 1F544B31C845D698EB31F2FF364F1162D32E7E58
sasl_domain: gmail.com
sasl_password: testpassword
sasl_username: testuser
securedrop_app_gpg_fingerprint: 1F544B31C845D698EB31F2FF364F1162D32E7E58
securedrop_app_gpg_public_key: sd_admin_test.pub
securedrop_app_https_certificate_cert_src: sd.crt
securedrop_app_https_certificate_chain_src: ca.crt
securedrop_app_https_certificate_key_src: key.asc
securedrop_app_https_on_source_interface: true
securedrop_supported_locales:
- de_DE
- es_ES
smtp_relay: smtp.gmail.com
smtp_relay_port: 587
ssh_users: sd
'''


def setup_function(function):
    global SD_DIR
    SD_DIR = tempfile.mkdtemp()
    ANSIBLE_BASE = '{0}/install_files/ansible-base'.format(SD_DIR)
    cmd = 'mkdir -p {0}/group_vars/all'.format(ANSIBLE_BASE).split()
    subprocess.check_call(cmd)
    for name in ['sd_admin_test.pub', 'ca.crt', 'sd.crt', 'key.asc']:
        subprocess.check_call('cp -r {0}/files/{1} {2}'.format(CURRENT_DIR,
                              name, ANSIBLE_BASE).split())
    for name in ['de_DE', 'es_ES', 'fr_FR', 'pt_BR']:
        dircmd = 'mkdir -p {0}/securedrop/translations/{1}'.format(
            SD_DIR, name)
        subprocess.check_call(dircmd.split())


def teardown_function(function):
    subprocess.check_call('rm -rf {0}'.format(SD_DIR).split())


def verify_username_prompt(child):
    child.expect("Username for SSH access to the servers:")


def verify_reboot_prompt(child):
    child.expect(
        "Daily reboot time of the server \(24\-hour clock\):", timeout=2)


def verify_ipv4_appserver_prompt(child):
    child.expect('Local IPv4 address for the Application Server\:', timeout=2)


def verify_ipv4_monserver_prompt(child):
    child.expect('Local IPv4 address for the Monitor Server\:', timeout=2)


def verify_hostname_app_prompt(child):
    child.expect('Hostname for Application Server', timeout=2)
    # For any default input, the text comes in the following format
    # child.expect takes a regular expression and child.expect_exact
    # does a string matching. That is why all such strings are matched
    # using child.expect_exact call
    # https://pexpect.readthedocs.io/en/stable/api/pexpect.html#pexpect.spawn.expect_exact
    child.expect_exact('\x1b[0ma\x1b[0mp\x1b[0mp\x1b[36D\x1b[36C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h', timeout=2)  # noqa: E501


def verify_hostname_mon_prompt(child):
    child.expect('Hostname for Monitor Server\:', timeout=2)


def verify_dns_prompt(child):
    child.expect('DNS server specified during installation\:', timeout=2)
    child.expect_exact('\x1b[0m8\x1b[0m.\x1b[0m8\x1b[0m.\x1b[0m8\x1b[0m.\x1b[0m8\x1b[49D\x1b[49C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501


def verify_app_gpg_key_prompt(child):
    child.expect('Local filepath to public key for SecureDrop Application GPG public key\:', timeout=2)  # noqa: E501


def verify_https_prompt(child):
    child.expect('Whether HTTPS should be enabled on Source Interface \(requires EV cert\)\:', timeout=2)  # noqa: E501


def verify_https_cert_prompt(child):
    child.expect('Local filepath to HTTPS certificate\:', timeout=2)


def verify_https_cert_key_prompt(child):
    child.expect('Local filepath to HTTPS certificate key\:', timeout=2)


def verify_https_cert_chain_file_prompt(child):
    child.expect('Local filepath to HTTPS certificate chain file\:', timeout=2)


def verify_app_gpg_fingerprint_prompt(child):
    child.expect('Full fingerprint for the SecureDrop Application GPG Key\:', timeout=2)  # noqa: E501


def verify_ossec_gpg_key_prompt(child):
    child.expect('Local filepath to OSSEC alerts GPG public key\:', timeout=2)  # noqa: E501


def verify_ossec_gpg_fingerprint_prompt(child):
    child.expect('Full fingerprint for the OSSEC alerts GPG public key\:', timeout=2)  # noqa: E501


def verify_admin_email_prompt(child):
    child.expect('Admin email address for receiving OSSEC alerts\:', timeout=2)  # noqa: E501


def verify_journalist_gpg_key_prompt(child):
    child.expect('Local filepath to journalist alerts GPG public key \(optional\)\:', timeout=2)  # noqa: E501


def verify_journalist_fingerprint_prompt(child):
    child.expect('Full fingerprint for the journalist alerts GPG public key \(optional\)\:', timeout=2)  # noqa: E501


def verify_journalist_email_prompt(child):
    child.expect('Email address for receiving journalist alerts \(optional\)\:', timeout=2)  # noqa: E501


def verify_smtp_relay_prompt(child):
    child.expect('SMTP relay for sending OSSEC alerts\:', timeout=2)
    child.expect_exact('[0ms\x1b[0mm\x1b[0mt\x1b[0mp\x1b[0m.\x1b[0mg\x1b[0mm\x1b[0ma\x1b[0mi\x1b[0ml\x1b[0m.\x1b[0mc\x1b[0mo\x1b[0mm\x1b[51D\x1b[51C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501


def verify_smtp_port_prompt(child):
    child.expect('SMTP port for sending OSSEC alerts\:', timeout=2)
    child.expect_exact('\x1b[0m5\x1b[0m8\x1b[0m7\x1b[39D\x1b[39C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501


def verify_sasl_domain_prompt(child):
    child.expect('SASL domain for sending OSSEC alerts\:', timeout=2)
    child.expect_exact('\x1b[0mg\x1b[0mm\x1b[0ma\x1b[0mi\x1b[0ml\x1b[0m.\x1b[0mc\x1b[0mo\x1b[0mm\x1b[47D\x1b[47C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501


def verify_sasl_username_prompt(child):
    child.expect('SASL username for sending OSSEC alerts\:', timeout=2)


def verify_sasl_password_prompt(child):
    child.expect('SASL password for sending OSSEC alerts\:', timeout=2)


def verify_ssh_over_lan_prompt(child):
    child.expect('will be available over LAN only\:', timeout=2)
    child.expect_exact('\x1b[0my\x1b[0me\x1b[0ms\x1b[37D\x1b[37C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501


def verify_locales_prompt(child):
    child.expect('Space separated list of additional locales to support')  # noqa: E501


def test_firstrun():
    cmd = os.path.join(os.path.dirname(CURRENT_DIR),
                       'securedrop_admin/__init__.py')
    child = pexpect.spawn('python {0} --root {1} sdconfig'.format(cmd, SD_DIR))
    verify_username_prompt(child)
    child.sendline('')
    verify_reboot_prompt(child)
    child.sendline('\b5')  # backspace and put 5
    verify_ipv4_appserver_prompt(child)
    child.sendline('')
    verify_ipv4_monserver_prompt(child)
    child.sendline('')
    verify_hostname_app_prompt(child)
    child.sendline('')
    verify_hostname_mon_prompt(child)
    child.sendline('')
    verify_dns_prompt(child)
    child.sendline('')
    verify_app_gpg_key_prompt(child)
    child.sendline('\b' * 14 + 'sd_admin_test.pub')
    verify_https_prompt(child)
    # Default answer is no
    child.expect_exact('\x1b[0mn\x1b[0mo\x1b[74D\x1b[74C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501
    child.sendline('')
    verify_app_gpg_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_ossec_gpg_key_prompt(child)
    child.sendline('\b' * 9 + 'sd_admin_test.pub')
    verify_ossec_gpg_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_admin_email_prompt(child)
    child.sendline('test@gmail.com')
    verify_journalist_gpg_key_prompt(child)
    child.sendline('')
    verify_smtp_relay_prompt(child)
    child.sendline('')
    verify_smtp_port_prompt(child)
    child.sendline('')
    verify_sasl_domain_prompt(child)
    child.sendline('')
    verify_sasl_username_prompt(child)
    child.sendline('testuser')
    verify_sasl_password_prompt(child)
    child.sendline('testpassword')
    verify_ssh_over_lan_prompt(child)
    child.sendline('')
    verify_locales_prompt(child)
    child.sendline('de_DE es_ES')
    time.sleep(2)  # Give time for validation
    with open(os.path.join(SD_DIR, 'install_files/ansible-base/group_vars/all/site-specific')) as fobj:    # noqa: E501
        data = fobj.read()
    assert data == OUTPUT1


def test_journalist_alert():
    cmd = os.path.join(os.path.dirname(CURRENT_DIR),
                       'securedrop_admin/__init__.py')
    child = pexpect.spawn('python {0} --root {1} sdconfig'.format(cmd, SD_DIR))
    verify_username_prompt(child)
    child.sendline('')
    verify_reboot_prompt(child)
    child.sendline('\b5')  # backspace and put 5
    verify_ipv4_appserver_prompt(child)
    child.sendline('')
    verify_ipv4_monserver_prompt(child)
    child.sendline('')
    verify_hostname_app_prompt(child)
    child.sendline('')
    verify_hostname_mon_prompt(child)
    child.sendline('')
    verify_dns_prompt(child)
    child.sendline('')
    verify_app_gpg_key_prompt(child)
    child.sendline('\b' * 14 + 'sd_admin_test.pub')
    verify_https_prompt(child)
    # Default answer is no
    child.expect_exact('\x1b[0mn\x1b[0mo\x1b[74D\x1b[74C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501
    child.sendline('')
    verify_app_gpg_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_ossec_gpg_key_prompt(child)
    child.sendline('\b' * 9 + 'sd_admin_test.pub')
    verify_ossec_gpg_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_admin_email_prompt(child)
    child.sendline('test@gmail.com')
    # We will provide a key for this question
    verify_journalist_gpg_key_prompt(child)
    child.sendline('sd_admin_test.pub')
    verify_journalist_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_journalist_email_prompt(child)
    child.sendline('test@gmail.com')
    verify_smtp_relay_prompt(child)
    child.sendline('')
    verify_smtp_port_prompt(child)
    child.sendline('')
    verify_sasl_domain_prompt(child)
    child.sendline('')
    verify_sasl_username_prompt(child)
    child.sendline('testuser')
    verify_sasl_password_prompt(child)
    child.sendline('testpassword')
    verify_ssh_over_lan_prompt(child)
    child.sendline('')
    verify_locales_prompt(child)
    child.sendline('de_DE es_ES')
    time.sleep(2)  # Give time for validation
    with open(os.path.join(SD_DIR, 'install_files/ansible-base/group_vars/all/site-specific')) as fobj:    # noqa: E501
        data = fobj.read()
    assert JOURNALIST_ALERT_OUTPUT == data


def test_enable_https():
    cmd = os.path.join(os.path.dirname(CURRENT_DIR),
                       'securedrop_admin/__init__.py')
    child = pexpect.spawn('python {0} --root {1} sdconfig'.format(cmd, SD_DIR))
    verify_username_prompt(child)
    child.sendline('')
    verify_reboot_prompt(child)
    child.sendline('\b5')  # backspace and put 5
    verify_ipv4_appserver_prompt(child)
    child.sendline('')
    verify_ipv4_monserver_prompt(child)
    child.sendline('')
    verify_hostname_app_prompt(child)
    child.sendline('')
    verify_hostname_mon_prompt(child)
    child.sendline('')
    verify_dns_prompt(child)
    child.sendline('')
    verify_app_gpg_key_prompt(child)
    child.sendline('\b' * 14 + 'sd_admin_test.pub')
    verify_https_prompt(child)
    # Default answer is no
    child.expect_exact('\x1b[0mn\x1b[0mo\x1b[74D\x1b[74C\x1b[?7h\x1b[0m\x1b[?12l\x1b[?25h')  # noqa: E501
    # We will press backspace twice and type yes
    child.sendline('\b\byes')
    verify_https_cert_prompt(child)
    child.sendline('sd.crt')
    verify_https_cert_key_prompt(child)
    child.sendline('key.asc')
    verify_https_cert_chain_file_prompt(child)
    child.sendline('ca.crt')
    verify_app_gpg_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_ossec_gpg_key_prompt(child)
    child.sendline('\b' * 9 + 'sd_admin_test.pub')
    verify_ossec_gpg_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_admin_email_prompt(child)
    child.sendline('test@gmail.com')
    # We will provide a key for this question
    verify_journalist_gpg_key_prompt(child)
    child.sendline('sd_admin_test.pub')
    verify_journalist_fingerprint_prompt(child)
    child.sendline('1F544B31C845D698EB31F2FF364F1162D32E7E58')
    verify_journalist_email_prompt(child)
    child.sendline('test@gmail.com')
    verify_smtp_relay_prompt(child)
    child.sendline('')
    verify_smtp_port_prompt(child)
    child.sendline('')
    verify_sasl_domain_prompt(child)
    child.sendline('')
    verify_sasl_username_prompt(child)
    child.sendline('testuser')
    verify_sasl_password_prompt(child)
    child.sendline('testpassword')
    verify_ssh_over_lan_prompt(child)
    child.sendline('')
    verify_locales_prompt(child)
    child.sendline('de_DE es_ES')
    time.sleep(2)  # Give time for validation
    with open(os.path.join(SD_DIR, 'install_files/ansible-base/group_vars/all/site-specific')) as fobj:    # noqa: E501
        data = fobj.read()
    assert HTTPS_OUTPUT == data


# The following is the minimal git configuration which can be used to fetch
# from the SecureDrop Github repository. We want to use this because the
# developers may have the git setup to fetch from git@github.com: instead
# of the https, and that requires authentication information.
GIT_CONFIG = u'''[core]
        repositoryformatversion = 0
        filemode = true
        bare = false
        logallrefupdates = true
[remote "origin"]
        url = https://github.com/freedomofpress/securedrop.git
        fetch = +refs/heads/*:refs/remotes/origin/*
'''

ORIGINAL_DIR = os.getcwd()
NEW_TMP_DIR = ""


# This class is to test all the git related operations.
class TestGitOperations:

    # We will create a new directory and copy the whole git repo
    # there. This will help us not to destroy the actual work environment.
    def setup_method(self, method):
        global NEW_TMP_DIR
        NEW_TMP_DIR = tempfile.mkdtemp()
        cmd = ['cp', '-r', '../', NEW_TMP_DIR]
        subprocess.check_call(cmd)
        os.chdir(os.path.join(NEW_TMP_DIR, 'admin'))
        subprocess.check_call('git reset --hard'.split())
        # Now we will put in our own git configuration
        with io.open('../.git/config', 'w') as fobj:
            fobj.write(GIT_CONFIG)
        # Let us move to an older tag
        subprocess.check_call('git checkout 0.6'.split())

    # We will go back to the original working directory when we are done.
    def teardown_method(self, method):
        global NEW_TMP_DIR
        os.chdir(ORIGINAL_DIR)
        # Let us remove the temporary directory
        subprocess.check_call('rm -rf {0}'.format(NEW_TMP_DIR).split())

    def test_check_for_update(self):
        cmd = os.path.join(os.path.dirname(CURRENT_DIR),
                           'securedrop_admin/__init__.py')
        fullcmd = 'python {0} --root {1} check_for_updates'.format(
                  cmd, os.path.join(NEW_TMP_DIR,
                                    'install_files/ansible-base '))
        child = pexpect.spawn(fullcmd)
        child.expect('Update needed', timeout=20)
