#!/usr/bin/env bash

if [ $# -eq 1 ]
then
	printf "Sourcing %s as the configuration file\n" $1
	source $1
else
 	printf "Usage: %s: [-s value] configfile\n" $(basename $0) >&2
        exit 2
fi

# Set SELinux context for Geonode httpd files
chcon -R -h -t httpd_sys_content_t $GEONODE_LIB
chcon -R -t httpd_sys_content_t $GEONODE_ETC

# Allow db and network relay connections
setsebool -P httpd_can_network_connect_db on
setsebool -P httpd_can_network_relay on

# Set http_tmp_exec (required for wsgi) if on RHEL6 or similar
RETV=`setsebool -P httpd_tmp_exec on > /dev/null 2>&1; echo $?`
# RHEL5 doesn't support httpd_tmp_exec, so create a new SELinux policy
if [ ! ${RETV} -eq 0 ]; then
cat > $GEONODE_SHARE/httpdtmpexec.te << EOF
module httpdtmpexec 1.0.0;

require {
        type httpd_t;
        type httpd_tmp_t;
        type httpd_tmpfs_t;
        class file execute;
}

#============= httpd_t ==============
allow httpd_t httpd_tmp_t:file execute;
allow httpd_t httpd_tmpfs_t:file execute;
EOF

checkmodule -M -m -o $GEONODE_SHARE/httpdtmpexec.mod $GEONODE_SHARE/httpdtmpexec.te
semodule_package --outfile $GEONODE_SHARE/httpdtmpexec.pp --module $GEONODE_SHARE/httpdtmpexec.mod
semodule -i $GEONODE_SHARE/httpdtmpexec.pp 

fi

sed '19i-A RH-Firewall-1-INPUT -m state --state NEW -m tcp -p tcp --dport 80 -j ACCEPT' -i /etc/sysconfig/iptables
service iptables restart
