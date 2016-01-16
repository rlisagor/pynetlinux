VAGRANT = vagrant

.PHONY: vagrant-up
vagrant-up:
	$(VAGRANT) up

.PHONY: vagrant-test
vagrant-test: vagrant-up
	$(VAGRANT) ssh -c "cd /vagrant && sudo /opt/pynetlinux/venv2/bin/py.test"
	$(VAGRANT) ssh -c "cd /vagrant && sudo /opt/pynetlinux/venv3/bin/py.test"
