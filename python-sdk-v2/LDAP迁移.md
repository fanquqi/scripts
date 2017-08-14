### LDAP 迁移 
> 迁移到nginxtest 服务器
> 主要分为三步：
> 1、LDAP服务部署
> 2、数据迁移
> 3、ldap-account-manager 安装
` apache端口号`：9000
 `配置目录`：/etc/openldap
 `数据目录`：/var/lib/ldap
 
- LDAP服务部署
参考：  http://docs.adaptivecomputing.com/viewpoint/hpc/Content/topics/1-setup/installSetup/settingUpOpenLDAPOnCentos6.htm
``` 
yum -y install openldap-servers migrationtools openldap openldap-clients
配置文件目录：/etc/openldap 
参考文档：http://www.learnitguide.net/2016/01/configure-openldap-server-on-rhel7.htm
开机启动：  systemctl enable slapd
启动：  systemctl start slapd
```
- 配置修改
    
- ldap-account-manager 安装
``` 
     yum install apache 
     systemctl enable httpd.service
     systemctl start httpd.service
     cd /data/soft/ && wget ftp://10.215.33.36/pub/ldap-account-manager-5.4.tar.bz2 ./
     tar -xjvf ldap-account-manager-5.4.tar.bz2 
     ./configure --prefix=/usr/local/lam --with-httpd-user=ldap --with-httpd-group=ldap
     make install 
     cd /usr/local/lam && mkdir config/pdf && mkdir config/profiles
     chown -R apache:apache /usr/local/lam
     配置文件修改(可以直接copy)
        - /usr/local/lam/conf/lam.conf
        - /usr/local/lam/conf/config.cfg
```
    - Apache配置修改
        首先/etc/httpd/httpd.conf 中 改为 listen 9000 监听9000端口
        然后再/etc/httpd/conf.d/ 中新建 lam_apche.conf 
        ``` bash
        [root@nginxtest conf.d]# cat lam_apache.conf
        Alias /lam /usr/local/lam
        <Directory /usr/local/lam>
         AllowOverride none
         Require all granted
        </Directory>
        ```
- 数据迁移
``` bash
青云：slapcat -l /root/ldapdump.raw
青云：egrep -v '^entryCSN:' < /root/ldapdump.raw > /root/ldapdump
拷贝/root/ldapdump到ucloud的nginxtest机器
停止openldap服务，systemctl stop slapd
ucloud导入：slapadd -l /root/ldapdump
```
`如果遇到如下错误`：需要删除/root/ldapdump 中的"dc=nodomain"数据。
``` 
slapadd: line 1: database #1 (dc=chunyu,dc=me) not configured to hold "dc=nodomain"; no database configured for that naming context
``` 
`如果遇到如下错误`：需要删除重复人记录
``` 
58ece50d hdb_monitor_db_open: monitoring disabled; configure monitor        database to enable
58ece50d => hdb_tool_entry_put: id2entry_add failed: BDB0067          DB_KEYEXIST: Key/data pair already exists (-30994)
58ece50d => hdb_tool_entry_put: txn_aborted! BDB0067 DB_KEYEXIST: Key/data pair already exists (-30994)
slapadd: could not add entry dn="uid=lixin,ou=people,dc=chunyu,dc=me" (line=1): txn_aborted! BDB0067 DB_KEYEXIST: Key/data pair already exists (-30994)
```
