Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.network "private_network", ip: "192.168.33.10"
  config.vm.network "private_network", ip: "192.168.34.10"

  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y python-virtualenv bridge-utils
    mkdir -p /opt/pynetlinux
    virtualenv /opt/pynetlinux/venv
    /opt/pynetlinux/venv/bin/pip install -r /vagrant/dev-requirements.txt
    chown -R vagrant:vagrant /opt/pynetlinux
  SHELL

end
