Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.network "private_network", ip: "192.168.34.10"

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y python3 python-virtualenv bridge-utils
    mkdir -p /opt/pynetlinux

    virtualenv --python python2 /opt/pynetlinux/venv2
    /opt/pynetlinux/venv2/bin/pip install -r /vagrant/dev-requirements.txt

    virtualenv --python python3 /opt/pynetlinux/venv3
    /opt/pynetlinux/venv3/bin/pip install -r /vagrant/dev-requirements.txt
    chown -R vagrant:vagrant /opt/pynetlinux
  SHELL

end
