VAGRANT = vagrant

.PHONY: vagrant-up
vagrant-up:
	$(VAGRANT) up

.PHONY: vagrant-test
vagrant-test: vagrant-up
	$(VAGRANT) ssh -c "cd /vagrant && sudo /opt/pynetlinux/venv/bin/py.test"
