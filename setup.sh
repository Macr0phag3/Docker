sudo yum -y install epel-release;
sudo yum install -y python-pip;
sudo yum install -y gcc;
sudo yum install -y wget;
sudo yum install -y git;
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python;
sudo pip install IPy;
sudo yum install -y python-devel
sudo pip install psutil
sudo pip install docker;
sudo pip install goto-statement;
sudo yum install -y yum-utils device-mapper-persistent-data lvm2;
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo;
sudo yum install -y docker-ce;
sudo systemctl start docker;
sudo systemctl enable docker;
docker version;
