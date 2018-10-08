# -*- coding: utf-8 -*-


from flask import Flask,render_template,request,send_file,make_response

from xlwt import Workbook
import paramiko
import time

app = Flask(__name__)


paramiko.util.log_to_file('paramiko.log')

@app.route('/')
def hello_world():
   return render_template("index.html")
@app.route('/home',methods=['GET','POST'])
def home():
    if request.method == 'POST':
        device=request.form['device']
        work=request.form['work']
        if device == 'fortigate' and work=='ports_check':
            return render_template("upload.html", work="fort_ports")
        if device=="fortigate" and work=="policy":
            return render_template("upload.html", work="fort_policy")
        if device=="dlink" and work=="ports_check":
            return render_template("upload.html",work="dlink_ports")
        if device=="fort" and work=="hardening":
            return render_template("upload.html",work="fort_hard")
        if device=="dlink" and work=="hardening":
            return render_template("upload.html",work="dlink_hard")
        if device=="cisco_asa" and work=="hardening":
            return render_template("upload.html",work="cisco_asa_hard")
        if device=="cisco_asa" and work=="ports_check":
            return render_template("upload.html",work="cisco_asa_ports")
        if device=="dell" and work=="ports_check":
            return render_template("upload.html",work="dell_ports")
        if device=="dell" and work=="hardening":
            return render_template("upload.html",work="dell_hard")


    return "Device is %s" %device



@app.route('/after_download_file_ports',methods=['POST'])
def fort_ports_download():
    return send_file('fort_ports.xls',as_attachment=True)

@app.route('/after_download_file_policy',methods=['POST'])
def fort_policy_download():
    return send_file('fort_policy.xls',as_attachment=True)

@app.route('/after_download_dlink_ports',methods=['POST'])
def dlink_ports_download():
    return send_file('dlink_ports.xls',as_attachment=True)

@app.route('/after_download_cisco_asa_ports',methods=['POST'])
def cisco_asa_ports_download():
    return send_file('cisco_asa_ports.xls',as_attachment=True)

@app.route('/after_download_dell_ports',methods=['POST'])
def dell_ports_download():
    return send_file('dell_ports.xls',as_attachment=True)



@app.route('/afterupload_dell_hard',methods=['POST'])
def dell_hard():
    f = request.files['file']
    username = request.form['username']
    password = request.form['password']

    for line in f:
        ipaddress = line.strip()
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ipaddress, username=username, password=password)
        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        print "configuring snmp"

        remote_connection.send("snmp-server community red-indian ro\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server host 45.127.100.36 traps version 2 red-indian\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server host 103.8.127.180 traps version 2 red-indian\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server contact ent-networks@ctrls.in\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        print "configuring Tacacs"
        remote_connection.send("aaa authentication login defaultList local local\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authentication login tacplus tacacs local none\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authentication enable enableList none\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authentication enable enableNetList none\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authentication enable tacp tacacs\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authorization exec dfltExecAuthList tacacs local\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authorization commands dfltCmdAuthList tacacs\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("tacacs-server host 103.241.139.66\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("timeout 5\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("key 7 D0ntknow123\n")

        remote_connection.send("tacacs-server timeout 2\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        print "configuring syslog"
        remote_connection.send("logging 182.18.174.185\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        print "NTP Configuration"
        remote_connection.send("sntp unicast client enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("sntp server 103.1.113.3\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("clock timezone 5 minutes 30 zone IST\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        ssh_client.close
    return render_template("index.html",work="success")


@app.route('/afterupload_dell_ports',methods=['POST'])
def dell_ports():
    f = request.files['file']
    username = request.form['username']
    password = request.form['password']
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')

    rowid = 0
    sheet1.write(0, 0, "IP Address")
    sheet1.write(0, 1, "Total Ports")
    sheet1.write(0, 2, "Unused Ports")
    sheet1.write(0, 3, "Used Ports")
    sheet1.write(0, 4, "ADM")

    for line in f:
        ipaddress = line.strip()
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=ipaddress, username=username, password=password)
        notconnected = 0
        disabled = 0
        connected = 0
        rowid = rowid + 1
        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("terminal length 0\n")
        remote_connection.send("show interface status\n")
        time.sleep(5)
        output = remote_connection.recv(9999999)

        for lin in output.split('\n'):
            if "up" in lin:
                connected = connected + 1
                continue
            if "down" in lin:
                notconnected = notconnected + 1
                continue
            if "ADM" in lin:
                disabled = disabled + 1
                continue

        total = connected + notconnected + disabled

        sheet1.write(rowid, 0, ipaddress)
        sheet1.write(rowid, 1, total)
        sheet1.write(rowid, 2, notconnected)
        sheet1.write(rowid, 3, connected)
        sheet1.write(rowid, 4, disabled)

        ssh_client.close

    wb.save('dell_ports.xls')
    return render_template("download_file.html",work="dell_ports")
@app.route('/afterupload_cisco_asa_ports',methods=['POST'])
def cisco_asa_ports():
    f = request.files['file']
    username = request.form['username']
    password = request.form['password']
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')

    rowid = 0
    sheet1.write(0, 0, "IP Address")
    sheet1.write(0, 1, "Total Ports")
    sheet1.write(0, 2, "Unused Ports")
    sheet1.write(0, 3, "Admin Down")
    for line in f:
        ipaddress = line.strip()
        if len(ipaddress)<4:
            break;
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ipaddress, username=username, password=password,timeout=200)
        except:
            continue
        notconnected = 0
        disabled = 0
        connected = 0
        rowid = rowid + 1
        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()
        time.sleep(2)
        remote_connection.send("en\n")
        time.sleep(1)
        remote_connection.send(password + "\n")
        time.sleep(2)
        remote_connection.send("terminal length 0 \n")
        time.sleep(5)

        output = remote_connection.recv(10000)
        print output

        remote_connection.send("show int ip brief\n")
        time.sleep(15)
        output = remote_connection.recv(100000)

        for line in output.split('\n'):
            parts = line.split()
            if len(parts) > 1:
                print parts[1]

            if "administratively down" in line:
                disabled += 1
                continue

            if "up" in line:
                connected += 1
                continue

            if "down" in line:
                notconnected += 1
                continue

        total = notconnected + disabled + connected
        print rowid
        sheet1.write(rowid, 0, ipaddress)
        sheet1.write(rowid, 1, total)
        sheet1.write(rowid, 2, notconnected)
        sheet1.write(rowid, 3, disabled)
        ssh_client.close

    wb.save('cisco_asa_ports.xls')
    return render_template("download_file.html",work="cisco_asa_ports")


@app.route('/afterupload_cisco_asa_hard',methods=['POST'])

def cisco_asa_hard():
    f = request.files['file']
    username = request.form['username']
    password = request.form['password']
    for line in f:
        ipaddress = line.strip()
        if len(ipaddress)<4:
            break;
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ipaddress, username=username, password=password,timeout=200)
        except:
            continue
        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()

        remote_connection.send("en\n")

        remote_connection.send(password + "\n")

        print "Configuring snmp"

        remote_connection.send("conf t\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("snmp-server host OUTSIDE 45.127.100.36 community red-indian version 2c\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server host OUTSIDE 202.65.156.10 community red-indian version 2c\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server host OUTSIDE 103.231.40.239 community red-indian version 2c\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server host OUTSIDE 103.241.139.69 community red-indian version 2c\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server host OUTSIDE 192.168.101.85 community red-indian version 2c\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("snmp-server contact ent-networks@ctrls.in\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server community red-indian\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server enable traps snmp authentication linkup linkdown coldstart\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server enable traps ipsec start stop\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server enable traps entity config-change fru-insert fru-remove\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("snmp-server enable traps remote-access session-threshold-exceeded\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("end\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        print "Configuring Tacacs"

        remote_connection.send("conf t\n")

        remote_connection.send("no aaa authentication ssh console LOCAL\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("username blackcat password D0ntknow123 pri 15\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa-server ACS protocol tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa-server ACS (outside) host 103.241.139.66\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("key D0ntknow123\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authentication ssh console ACS LOCAL\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authentication http console ACS LOCAL\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authentication enable console ACS LOCAL\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa authorization command LOCAL\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("aaa accounting ssh console ACS\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("end\n")

        print "Configuring syslog"

        remote_connection.send("conf t\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("logging host OUTSIDE 103.241.182.123\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("end\n")
        print "configuring NTP"
        remote_connection.send("conf t\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("ntp server 202.65.156.10 source OUTSIDE\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("clock timezone IST 5 30\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("end\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        ssh_client.close
    return render_template("index.html",work="success")



@app.route('/afterupload_dlink_hard',methods=['POST'])
def dlink_hard():
    f = request.files['file']
    username = request.form['username']
    password = request.form['password']

    for line in f:
        ipaddress = line.strip()
        if len(ipaddress)<4:
            break;
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ipaddress, username=username, password=password,timeout=200)
        except:
            continue
        notconnected = 0
        disabled = 0
        connected = 0

        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()
        time.sleep(2)
        output = remote_connection.recv(1000)
        print output
        print "Configuring storm"
        remote_connection.send( "config traffic control 1:1-24 broadcast enable action drop broadcast_threshold 510 multicast_threshold 510 countdown 0 time_interval 5\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        print "Username Configuration"
        remote_connection.send("create account admin Bluewhale\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("E&t]C$4c@Vs}\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("E&t]C$4c@Vs}\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable password encryption\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        print "configuring snmp"
        remote_connection.send("delete snmp community public\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("delete snmp community private\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("delete snmp user initial\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("delete snmp group initial\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("delete snmp view restricted all\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("delete snmp view CommunityView all\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("create snmp group red-indian v1 read_view CommunityView notify_view CommunityView\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create snmp group redi-ndian v2c read_view CommunityView notify_view CommunityView\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create snmp community red-indian view CommunityView read_write\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create snmp user initial initial\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create snmp host 45.127.100.36 v2c  red-indian\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create snmp host 45.127.100.36 v2c  redindian\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable community_encryption\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config snmp system_contact ent-networks@ctrls.in\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable snmp\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable snmp traps\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable snmp authenticate_traps\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable snmp linkchange_traps\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("save\n")
        print "configuring Tacacs"
        remote_connection.send("enable authen_policay\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create authen server_host 103.241.139.66 protocol tacacs+ port 49 key D0ntknow123 timeout 30 retransmit 2\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen server_group tacacs+ delete server_host 103.241.139.66 protocol tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen server_group tacacs+ add server_host 103.241.139.66 protocol tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen_login default method  local\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create authen_login method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen_login method_list_name Tacacs+ method tacacs+ local\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen_enable default method  local_enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create authen_enable method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen_enable method_list_name Tacacs+ method tacacs+ local_enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen application telnet login method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen application telnet enable method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen application ssh login method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen application ssh enable method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen application http login method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen application http enable method_list_name Tacacs+\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen parameter response_timeout 30\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config authen parameter attempt 3\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("save\n")

        print "Configuring syslog"

        remote_connection.send("config log_save_timing on_demand\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable syslog\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config system_severity trap information\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config system_severity log information\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("create syslog host 1 ipaddress 103.1.113.5 severity informational facility local0 udp_port 514 state enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("save\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        print "Configuring time"
        remote_connection.send("config time_zone operator + hour 5 min 30\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config dst disable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("enable sntp\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config sntp primary 103.1.113.3 secondary 202.65.156.10 poll-interval 60\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("save\n")
        ssh_client.close
        return render_template("index.html",work="success")

@app.route('/afterupload_fort_hard',methods=['POST'])
def fort_hard():
    f = request.files['file']
    username = request.form['username']
    password = request.form['password']

    for line in f:
        ipaddress = line.strip()
        if len(ipaddress)<4:
            break;
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ipaddress, username=username, password=password,timeout=200)
        except:
            continue

        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("a")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        print "banner Configuration"
        remote_connection.send("config system  global\n")
        remote_connection.send("set pre-login-banner enable\n")
        remote_connection.send("set post-login-banner enable\n")

        print "username Configuration"
        remote_connection.send("config system admin\n")
        remote_connection.send("edit Bluewhale\n")
        remote_connection.send("set vdom root\n")
        remote_connection.send("set password E&t]C$4c@Vs}\n")
        remote_connection.send("set trusthost1 182.18.148.101 255.255.255.255\n")
        remote_connection.send("set trusthost2 202.65.148.252 255.255.255.255\n")
        remote_connection.send("set trusthost3 45.127.100.36  255.255.255.255\n")
        remote_connection.send("set trusthost4 103.8.127.180  255.255.255.255\n")
        remote_connection.send("set trusthost5 202.65.156.10  255.255.255.255\n")
        remote_connection.send("set trusthost5 103.1.113.3  255.255.255.255\n")
        remote_connection.send("set accprofile super_admin\n")
        remote_connection.send("end\n")
        print "snmp COnfiguration"

        remote_connection.send("config system snmp community\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("edit 1\n")

        remote_connection.send("set name red-indian\n ")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("set status enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("config hosts\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("edit 1\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("set ip 45.127.100.36 255.255.255.255\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("next\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("edit 2\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("set ip 103.8.127.180 255.255.255.255\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("next\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("end\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("set query-v1-status disable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("set query-v2c-status enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("set trap-v1-status disable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("set trap-v2c-status enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send(
            "set events cpu-high mem-low vpn-tun-up vpn-tun-down ha-member-up ha-member-down log-full intf-ip av-virus av-oversize av-pattern av-fragmented ips-signature ips-anomaly av-conserve av-bypass av-oversize-passed av-oversize-blocked ips-pkg-update ent-conf-change ha-switch ha-hb-failure\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("next\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("end\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output

        remote_connection.send("config system snmp sysinfo\n")

        output = remote_connection.recv(1000)
        print output
        remote_connection.send("set status enable\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("set contact-info ent-networks@ctrls.in\n")
        time.sleep(1)
        output = remote_connection.recv(1000)
        print output
        remote_connection.send("end\n")

        print "configuring Syslog"
        remote_connection.send("config log syslogd setting\n")
        remote_connection.send("set status enable\n")
        remote_connection.send("set server 182.18.174.185\n")
        remote_connection.send("set reliable disable\n")
        remote_connection.send("set port 514\n")
        remote_connection.send("set facility local7\n")
        remote_connection.send("end\n")
        remote_connection.send("config log eventfilter\n")
        remote_connection.send("set event enable\n")
        remote_connection.send("set system enable\n")
        remote_connection.send("set vpn enable\n")
        remote_connection.send("set user enable\n")
        remote_connection.send("set router enable\n")
        remote_connection.send("set wireless-activity disable\n")
        remote_connection.send("set wan-opt enable\n")
        remote_connection.send("set endpoint enable\n")
        remote_connection.send("set ha enable\n")
        remote_connection.send("end\n")

        print "Configuring tacacs"
        remote_connection.send("config user tacacs+\n")
        remote_connection.send("edit tacacs1\n")
        remote_connection.send("set server 103.241.139.66\n")
        remote_connection.send("set key D0ntknow123\n")
        remote_connection.send("next\n")
        remote_connection.send("end\n")
        remote_connection.send("config user group\n")
        remote_connection.send("edit user_admin\n")
        remote_connection.send("set member tacacs1\n")
        remote_connection.send("next\n")
        remote_connection.send("end\n")
        remote_connection.send("edit Tacacs\n")
        remote_connection.send("set remote-auth enable\n")
        remote_connection.send("set trusthost1 182.18.148.101 255.255.255.255\n")
        remote_connection.send("set trusthost2 202.65.148.252 255.255.255.255\n")
        remote_connection.send("set accprofile super_admin\n")
        remote_connection.send("set wildcard enable\n")
        remote_connection.send("set remote-group user_admin\n")
        remote_connection.send("next\n")
        remote_connection.send("end\n")

        print "Configuring DNS"

        remote_connection.send("config system dns\n")
        remote_connection.send("set primary 202.65.156.10\n")
        remote_connection.send("set secondary 103.1.113.3\n")
        remote_connection.send("end\n")

        ssh_client.close
    return render_template('index.html',work="success")

@app.route('/afterupload_dlink_ports',methods=['POST'])
def dlink_ports():
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')

    rowid = 0
    sheet1.write(0, 0, "IP Address")
    sheet1.write(0, 1, "Total Ports")
    sheet1.write(0, 2, "Unused Ports")
    sheet1.write(0, 3, "Disabled Ports")
    sheet1.write(0, 4, "Used Ports")
    f = request.files['file']
    username = request.form['username']
    password = request.form['password']


    for line in f:
        ipaddress = line.strip()
        if len(ipaddress)<4:
            break;
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ipaddress, username=username, password=password,timeout=200)
        except:
            continue
        notconnected = 0
        disabled = 0
        connected = 0
        rowid = rowid + 1
        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()
        time.sleep(2)
        poutput = remote_connection.recv(1000)
        remote_connection.send("show ports\n")

        time.sleep(2)

        output = remote_connection.recv(10000)
        while poutput != output:
            poutput = output
            for line in output.split('\n'):

                if "Link Down" in line:
                    notconnected += 1
                    continue
                if "Full" in line:
                    connected += 1
                    continue
                if "disabled" in line:
                    disabled += 1
                    continue

        remote_connection.send("n")

        time.sleep(2)
        output = remote_connection.recv(10000)


        notconnected = notconnected - 4
        total = notconnected + disabled + connected
        print rowid
        sheet1.write(rowid, 0, ipaddress)
        sheet1.write(rowid, 1, total)
        sheet1.write(rowid, 2, notconnected)
        sheet1.write(rowid, 3, disabled)
        sheet1.write(rowid, 4, connected)
        ssh_client.close

    wb.save('dlink_ports.xls')

@app.route('/afterupload_fort_policy',methods=['POST'])
def fort_policy():
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')

    rowid = 0
    sheet1.write(0, 0, "IP Address")
    sheet1.write(0, 1, "Policy-ID")
    sheet1.write(0, 2, "Srcintf")
    sheet1.write(0, 3, "Dstintf")
    sheet1.write(0, 4, "Srcaddr")
    sheet1.write(0, 5, "Dstaddr")
    sheet1.write(0, 6, "Action")
    sheet1.write(0, 7, "Schedule")
    sheet1.write(0, 8, "Service")

    f = request.files['file']
    username = request.form['username']
    password = request.form['password']


    for line in f:

        ipaddress = line.strip()
        if len(ipaddress)<4:
            break;
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ipaddress, username=username, password=password, timeout=300)
        except:
            continue

        print "Connection successfull", ipaddress

        remote_connection = ssh_client.invoke_shell()
        time.sleep(1)
        output = remote_connection.recv(10000)
        remote_connection.send("a\n")
        time.sleep(1)
        output = remote_connection.recv(10000)
        print output
        remote_connection.send("config system console\n")
        remote_connection.send("set output standard\n")
        remote_connection.send("end\n")
        time.sleep(1)
        output = remote_connection.recv(10000)
        print output

        remote_connection.send("show firewall policy\n")
        time.sleep(70)
        output = remote_connection.recv(999999999)
        print len(output)

        for l in output.split('\n'):
            if "edit" in l:
                rowid = rowid + 1
                sheet1.write(rowid, 0, ipaddress)
                policy = l.strip('edit ')
                try:
                    sheet1.write(rowid, 1, policy)
                except:
                    continue;
            if "set srcintf " in l:
                srs = l.strip('set srcintf')
                try:
                    sheet1.write(rowid, 2, srs)
                except:
                    continue;
            if "set dstintf " in l:
                df = l.strip('set dstintf')
                try:
                    sheet1.write(rowid, 3, df)
                except:
                    continue;
            if "set srcaddr " in l:
                src = l.strip('set srcaddr')
                try:
                    sheet1.write(rowid, 4, src)
                except:
                    continue;
            if "set dstaddr" in l:
                dst = l.strip('set dstaddr')
                try:
                    sheet1.write(rowid, 5, dst)
                except:
                    continue;
            if "set action accept" in l:

                act = l.strip('set action accept')
                try:
                    sheet1.write(rowid, 6, "accept")
                    continue;
                except:
                    print "error ", rowid
                    continue;
            if "set action deny" in l:
                try:
                    sheet1.write(rowid, 6, "deny")
                except:
                    continue;
            if "set schedule" in l:
                sch = l.strip('set schedule')
                try:
                    sheet1.write(rowid, 7, sch)
                except:
                    continue;
            if "set service" in l:
                ser = l.strip('set service')
                try:
                    sheet1.write(rowid, 8, ser)
                except:
                    print "error writng"
                    print rowid;
                    continue;

        ssh_client.close

    wb.save('fort_policy.xls')
    return render_template('download_file.html',work="fort_policy")


@app.route('/afterupload_fort_ports',methods=['POST'])
def run():
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')

    sheet1.write(0, 0, "IP Address")
    sheet1.write(0, 1, "Version")
    sheet1.write(0, 2, "Serial_NO")
    sheet1.write(0, 3, "Total Ports")
    sheet1.write(0, 4, "used ports")
    sheet1.write(0, 5, "unused Ports")
    f=request.files['file']
    username=request.form['username']
    password=request.form['password']
    rowid = 0
    for line in f:
        ipaddress = line.strip()
        if len(ipaddress)<4:
            break;
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh_client.connect(hostname=ipaddress, username=username, password=password,timeout=200)
        except:
            continue
        notconnected = 0
        disabled = 0
        connected = 0
        rowid = rowid + 1


        remote_connection = ssh_client.invoke_shell()
        time.sleep(2)
        remote_connection.send("a\n")
        poutput = remote_connection.recv(1000)
        remote_connection.send("config system console\n")
        remote_connection.send("set output standard\n")
        remote_connection.send("end\n")
        time.sleep(1)
        output = remote_connection.recv(10000)


        remote_connection.send("get system status\n")

        time.sleep(5)
        output = remote_connection.recv(10000)
        version = "not found"
        serial = "not found"
        for line in output.split('\n'):
            if "Version:" in line:
                version = line.lstrip('Version:')

            if "Serial-Number:" in line:
                serial = line.lstrip('Serial-Number:')

        sheet1.write(rowid, 0, ipaddress)
        sheet1.write(rowid, 1, version)
        sheet1.write(rowid, 2, serial)
        remote_connection.send("get system interface\n")
        time.sleep(5)

        output = remote_connection.recv(100000)
        for line in output.split('\n'):
            if "name: ssl.root" in line or "name: mesh.root" in line:
                continue
            if "status: down" in line:
                notconnected += 1
                continue
            if "status: up" in line:
                connected += 1
                continue

        total = notconnected + connected

        sheet1.write(rowid, 3, total)
        sheet1.write(rowid, 4, notconnected)
        sheet1.write(rowid, 5, connected)

        ssh_client.close
    wb.save('fort_ports.xls')

    return render_template('download_file.html',work="fort_ports")

if __name__ == '__main__':
   app.run()