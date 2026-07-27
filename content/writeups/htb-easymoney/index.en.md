---
title: "HTB DFIR Sherlock: EasyMoney"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-05-10
source: Medium
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

# HTB DFIR Sherlock: EasyMoney

This time I am going to tackle a medium difficulty challenge. It is a Windows incident response scenario where a user was deceived by a malicious shortcut, leading to full compromise of the host. This challenge features event log analysis, artifact investigation, and a bit of binary analysis. Let’s dive into how John got baited by a malicious file!

---

> Task 1: At what exact time did the user execute the malicious shortcut file?

The UserAssist artifact is logging any application executed from the GUI (aka _explorer.exe_). It also keep track of useful data such as execution count or last execution timestamp. In this case, it’s exactly what we need! So I got [Registry Explorer](https://ericzimmerman.github.io/#!index.md) running to load the following hive:

```
#registry location 
cd C:\Windows\System32\config\SOFTWARE
#hive path to load in Registry Explorer
SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\UserAssist
```

And here comes one _very_ suspicious shortcut **lnk**.

{{< image src="images/User_Assist_extract_showing_execution_ti_1008.png" alt="User Assist extract showing execution time of malicious 2025-GiveAways.lnk" caption="Execution time of malicious 2025-GiveAways.lnk" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025–01–26 16:17:15
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: The previous malicious file executed an initial payload. What is the full path of this payload?

The first thing to check when working on this type of challenge is the **Powershell event logs** located in (located in `C:\Windows\System32\winevt\logs`). More often than not, part of the payload can be recovered from these logs. This case is no exception. 

Shortly after the shortcut execution timestamp, a Windows PowerShell script was executed, running the following command:

{{< image src="images/Powershell_command_executed_by_malicious_6205.png" alt="Powershell command executed by malicious shortcut" caption="Powershell command executed (source: Windows PowerShell.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Temp\svch0st.exe
{{< /admonition >}}

The GitHub repository is no longer accessible, so we cannot analyze the binary directly. We will need to trace its activity through the event logs. GitHub was likely used as a legitimate download source to avoid raising suspicion.

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: At what timestamp did the payload execute and grant the attacker shell access?

Knowing the name of the downloaded executable, we can look in the **prefetch database** to find the execution evidence. To parse these files, you would have to execute:

```powershell
PECmd.exe -d "EasyMoney\C\Windows\prefetch" --csv EasyMoney_Output
```

{{< image src="images/Execution_proof_of_svch0st_exe_in_prefet_275.png" alt="Execution proof of svch0st.exe in prefetch database" caption="Execution proof of svch0st.exe (source: C:\Windows\prefetch)" >}}

on the screenshot above, we have the precise execution time of the payload.

{{< admonition type=success title="FLAG" open=false >}}
2025–01–26 16:17:54
{{< /admonition >}}

Out of curiosity, let’s check what happens right after the malicious binary was executed. By staying in our prefetch database, we can see some more recon steps: **checking the current user** and the **system specifications**.

{{< image src="images/Extra_recon_steps_ran_by_the_malicious_b_3677.png" alt="Extra recon steps ran by the malicious binary" caption="Extra recon steps ran by the malicious binary (source: C:\Windows\prefetch)" >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: What is the command line the attacker used to enumerate installed packages on the system?

In the **Powershell event log**, we can see an extra powershell command invoked that list installed software. On our compromission timeline, it appears at 2025–01–26 16:19:29, which is shortly after the initial access.

{{< image src="images/Powershell_package_enumeration_from_Wind_5392.png" alt="Powershell package enumeration from Windows PowerShell.evtx" caption="Powershell package enumeration (source: Windows PowerShell.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -Command Get-Package
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: Which application did the attacker identify as vulnerable?

Just as in Task 3, we are going to review the **prefetch database** to find which program was started after the package enumeration. And it happened that a non-standard program is started, probably by the intruder: **YandexBrowser**.

{{< image src="images/YandexBrowser_execution_proof_from_prefe_9099.png" alt="YandexBrowser execution proof from prefetch database" caption="YandexBrowser execution proof (source: C:\Windows\prefetch)" >}}

Just as the name suggests, yes, it is a **web browser** 😲! It is the largest search engine in Russia, launched in 1997. Yandex also has the largest ridesharing company in Russia - yes, I know it’s completely irrelevant but I needed to put it somewhere.

{{< admonition type=success title="FLAG" open=false >}}
YandexBrowser
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: What version of that vulnerable application did the attacker identify?

This one is a quick win, just looking at the previous task we can see that the version is embedded into the _Service_Update.exe_ path (cf. previous Task screenshot).

{{< admonition type=success title="FLAG" open=false >}}
24.4.5.498
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: What is the CVE associated with this vulnerability?

A bit of Googling later with the keywords “yandex 24.4.5.498 cve” we find this CVE ID: [**CVE-2024–6473**](https://nvd.nist.gov/vuln/detail/CVE-2024-6473). This version is vulnerable to a DLL Hijacking vulnerability and the attacker surely used this to elevate its privilege. We may be faced with a malicious DLL that will be loaded alongside Yandex in the `%LOCALAPPDATA%\Yandex\YandexBrowser\Application` directory (cf. [POC on Github](https://github.com/12345qwert123456/CVE-2024-6473-PoC)).

{{< admonition type=success title="FLAG" open=false >}}
CVE-2024–6473
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: What is the name of the legitimate binary that the attacker used to deliver the malicious payload and establish persistence on the compromised system?

Prefetch FTW, at 16:36:11, a legitimate windows networking tool was used by the attacker. It can be used to [download file](https://lolbas-project.github.io/) on the system.

{{< admonition type=success title="FLAG" open=false >}}
certutil.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: What is the name of the malicious Portable Executable (PE) file that enabled him to accomplish his objective?

Since _cmd.exe_ was used to invoke _certutil.exe_ (and not powershell.exe) we don’t have the URI **not registered in an EVTX log**. However, **certutil has a cache folder** where it store the downloaded files. If you know about it, it’s in `%LOCALAPPDATA%LOW\Microsoft\CryptnetUrlCache\Content`.

If you didn’t know this, the MFT could’ve helped you there:

{{< image src="images/MFT_extract_showing_download_of_proxydll_5764.png" alt="MFT extract showing download of proxydll and payload" caption="MFT extract showing download of proxydll and payload" >}}

New entries in the MFT appears right after _certutil.exe_ execution. We can see that a copy of the metadata and of the file content is made in our CryptnetUrlCache folder. The original file can be spotted using file size. For example here, a malicious **wldp.dll** was downloaded in `YandexBrowser\Application` and cached as `A16B2E6DE64B13EDF2C00F32C4559930`.

{{< admonition type=success title="FLAG" open=false >}}
wldp.dll
{{< /admonition >}}

To collect a useful IOC, we can look for their metadata to find where they come from:

```powershell
Get-ChildItem A16*,DE6* | ForEach-Object { strings.exe $_.FullName }
#output:
http://18.192.12.126:8000/wldp.dll
http://18.192.12.126:8000/yanda.tmp
```

So I assume that we’re facing a python simple HTTP that serves the two malicious files on the IP address **18.192.12.126**.

To go back to the compromission timeline, we have a **wldp.dll** download, that is the malicious file used to exploit the DLL hijacking vulnerability (cf. Task 7). And we have a **yanda.tmp** file that is probably our final stage payload. We’re gonna dig into that later 🔮

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: What is the SHA-256 hash of that malicious file?

So let’s SHA256 hash the **wldp.dll** found in `CryptnetUrlCache\Content`:

{{< admonition type=success title="FLAG" open=false >}}
A1A17EBD90610D808E761811D17DA3143F3DE0D4CC5EE92BD66000DCA87D9270
{{< /admonition >}}

That’s fine we got the flag, but WTF is this file? When loading the DLL in [PE-bear](https://github.com/hasherezade/pe-bear), we see in the **debug section** that the .pdb is located in `Desktop\ProxyDll\distrib\03_lolnope\x64_debug\version.pdb`. What an odd filename 😱! When you Google the string `03_lolnope`, it leads straight to a [GitHub repository](https://github.com/advancedmonitoring/ProxyDll) showcasing a Proxy DLL project. That’s likely what’s loaded our final payload through the DLL Hijacking.

{{< style "height:2rem;" >}}{{< /style >}}
> Task 11: How many milliseconds of cumulative coded sleep delays occurred before the C2 binary provided a shell after the vulnerable application was launched?

The binary isn’t stripped so the disassembling won’t be too messy if the binary was compiled without obfuscation as in the original repository.

```
#source: CryptnetUrlCache\Content
file A16B2E6DE64B13EDF2C00F32C4559930
#output
PE32+ executable (DLL) (GUI) x86-64, for MS Windows
```

I’m not a reverse engineer but this part only require some thinking. Let’s guess how delay can be called by the developper? I’m gonna try “sleep” 🤓. So in IDA we Alt+T and search for this string.

{{< image src="images/IDA_screenshot_displaying_occurrence_of__1481.png" alt="IDA screenshot displaying occurrence of sleep string" caption="Found sleep strings in wldp.dll" >}}

First occurrence in _sub_1800748E0_ is the following. It starts Yandex browser after a sleep time of 10 000ms.

{{< image src="images/IDA_screenshot_displaying_a_sleep_of_100_6952.png" alt="IDA screenshot displaying a sleep of 10000ms" caption="First sleep in wldp.dll, after browser.exe launch" >}}

The second appearance of Sleep is just after the first one. It sleeps 1 000ms before running **yanda.tmp** (that is our final stage payload).

{{< image src="images/IDA_screenshot_displaying_a_sleep_of_100_6013.png" alt="IDA screenshot displaying a sleep of 1000ms" caption="Second sleep in wldp.dll, after yanda.tmp launch" >}}

So overall, we have a sleep counter of **11000 milliseconds**before the shell is beaconing back to the attacker.

{{< admonition type=success title="FLAG" open=false >}}
11000
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 12: What is the mutex name used to ensure only one instance of the C2 binary runs at a time?

Searching strings in IDA, we try _mutex_ and BINGO we found a mutex name spawned by _CreateMutexW_.

{{< image src="images/IDA_screenshot_the_mutex_name_used_by_th_2294.png" alt="IDA screenshot the mutex name used by the proxydll" caption="Found the mutex name in wldp.dll" >}}

{{< admonition type=success title="FLAG" open=false >}}
Global\\YandaExeMutex
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 13: What is the full path of the Command and Control (C2) Binary?

Looking back at Task 9 analysis, we already have the answer to this question (thanks to our thorough analysis 🤓). I’m just pasting a MFT extract screenshot for the lazy ones.

{{< image src="images/MFT_extract_showing_download_of_yanda_tm_1887.png" alt="MFT extract showing download of yanda.tmp" caption="MFT extract showing download of yanda.tmp" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\Administrator\AppData\Local\Temp\yanda.tmp
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 14: What is the name of the C2 framework used by the attacker?

From this point, I’m getting bored and we’ve done most of the work so I’m just going to ask VirusTotal for some help. So let’s paste our SHA256 hash retrieved previously and review the report.

{{< image src="images/VT_report_on_yanda_tmp_7433.png" alt="VT report on yanda.tmp" caption="VT report on yanda.tmp" >}}

And I think it is clear that we are facing a **sliver payload** ([full report here](https://www.virustotal.com/gui/file/a64be5730df8ea564739b297be23fa5a27abf2b3f5616dc4d8603b32801a7c5b/detection)).

{{< admonition type=success title="FLAG" open=false >}}
sliver
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
We also could’ve thrown a bunch of Yara detection rules on the binary to learn that it’s indeed a sliver generated payload.
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 15: What is the IP address and port number of the malicious C2 server used by the attacker?

Switching to the [behavior tab](https://www.virustotal.com/gui/file/a64be5730df8ea564739b297be23fa5a27abf2b3f5616dc4d8603b32801a7c5b/behavior) of the VT report, we discover the IP where both the proxy dll and the sliver payload were downloaded from. It’s not only a payload dropper but also the C2 VPS (listening on port 8888).

{{< image src="images/VT_report_on_yanda_tmp__network_comm_tab_7967.png" alt="VT report on yanda.tmp (network comm tab)" caption="VT report on yanda.tmp (network comm tab)" >}}

{{< admonition type=success title="FLAG" open=false >}}
18.192.12.126:8888
{{< /admonition >}}

---

Taking a step back at this report, I feel pleased to have solved it. It was a lengthy windows forensic investigation where I did not learn much, but where I sharpened my analysis skills a ton!

_NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content._

{{< image src="images/EasyMoney_success_banner_2733.png" alt="EasyMoney success banner" caption="EasyMoney success banner" >}}
