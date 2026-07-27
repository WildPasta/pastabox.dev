---
title: "HTB DFIR Sherlock: SmartyPants"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-02-27
source: Medium
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

# HTB DFIR Sherlock: SmartyPants

After solving EasyMoney, I had to chill out doing an easy box. That is why we are now analysing SmartyPants’ event logs. This is an easy challenge where you have to follow the actions of an attacker, find the files he has exfiltrated and how he tried to cover his tracks.

---

> Task 1: The attacker logged in to the machine where Dutch saves critical files, via RDP on 24th January 2025. Please determine the timestamp of this login.

It’s time to find attacker’s initial access! Since it’s an easy challenge, we already have the hint that it’s gonna be on the 24th of January. So we’re going to filter out on the EVTX called RemoteDesktopServices to list the successful RDP connections.

{{< image src="images/Screenshot_showing_attacker_s_first_RDP__2686.png" alt="Screenshot showing attacker’s first RDP connection in RemoteDesktopServices.evtx" caption="Attacker’s first RDP connection (source: RemoteDesktopServices.evtx)" >}}

So OK the timestamp flag is valid: **2025–01–24 10:15:14**, but we were lucky that there one only one occurrence of that event 🍀!

Let’s add the LocalSessionManager logs to our Timeline Explorer. Doing that extra step, we discover that Dutch first logged in at 2025–01–24 10:06:24 as Session ID 2.

{{< image src="images/Screenshot_showing_attacker_s_first_RDP__6516.png" alt="Screenshot showing attacker’s first RDP connection in LocalSessionManager.evtx" caption="Attacker’s first RDP connection (source: LocalSessionManager.evtx)" >}}

Later, we can see that the user Dutch is being disconnected to be replaced by another user which is: DUTCH 🤯! So it is likely that the legitimate Dutch got kicked out by the intruder.

{{< image src="images/Screenshot_showing_attacker_disconnectin_2430.png" alt="Screenshot showing attacker disconnecting Dutch in LocalSessionManager.evtx" caption="Attacker disconnected DUTCH user (source: LocalSessionManager.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025-01-24 10:15:14
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: The attacker downloaded a few utilities that aided them for their sabotage and extortion operation. What was the first tool they downloaded and installed?

From this point on, the challenge becomes boring 😴. It’s mentioned in the challenge introduction that smartscreen event log is enabled on the domain. And guess what? Every other flag can be found in the **SmartScreen Debug EVTX**!

For example, the utility we are looking for here is the third event (at 2025–01–24 10:17:23) in the SmartScreen EVTX: **WinRAR**.

{{< image src="images/Screenshot_showing_WinRAR_execution_trac_5605.png" alt="Screenshot showing WinRAR execution trace (source: SmartScreenDebug.evtx)" caption="WinRAR execution trace (source: SmartScreenDebug.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
WinRAR
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: They then proceeded to download and then execute the portable version of a tool that could be used to search for files on the machine quickly and efficiently. What was the full path of the executable?

Below our dear WinRAR, we find a weird program executed by the user: **Everything.exe**

```json
#source: SmartScreenDebug.evtx
{"EventData":{"Data":{"@Name":"Data","#text":"{\"$type\":\"isFileSupported\",\"executionTime\":\"5045\",\"path\":\"C:\\\\Program Files\\\\WinRAR\\\\WinRAR.exe\",\"size\":\"3289752\"}"}}}
{"EventData":{"Data":{"@Name":"Data","#text":"{\"$type\":\"isFileSupported\",\"executionTime\":\"8701\",\"path\":\"C:\\\\Users\\\\Dutch\\\\Downloads\\\\Everything.exe\",\"size\":\"1778192\"}"}}}
```

{{< admonition type=success title="FLAG" open=false >}}
Everything.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: What is the execution time of the tool from task 3?

The timestamp can be found in the log displayed in Task 3.

{{< admonition type=success title="FLAG" open=false >}}
2025–01–24 10:17:33
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: The utility was used to search for critical and confidential documents Sstored on the host, which the attacker could steal and extort the victim. What was the first document that the attacker got their hands on and breached the confidentiality of that document?

Just after the finding of _Everything.exe_, we locate two PDFs (still in SmartScreenDebug).

{{< image src="images/Screenshot_showing_PDFs_opening_trace__s_2732.png" alt="Screenshot showing PDFs opening trace (source: SmartScreenDebug.evtx)" caption="PDFs opening trace (source: SmartScreenDebug.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\Dutch\Documents\2025- Board of directors Documents\Ministry Of Defense Audit.pdf
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: Find the name and path of second stolen document as well.

The second PDF is the flag here.

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\Dutch\Documents\2025- Board of directors Documents\2025-BUDGET-ALLOCATION-CONFIDENTIAL.pdf
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: The attacker installed a Cloud utility as well to steal and exfiltrate the documents. What is name of the cloud utility?

Right after the two PDF we found, there is an execution of [MEGAsync](https://github.com/meganz/MEGAsync) which is an utility to synchronize file across devices. Here it has been used for exfiltration purpose.

```json
#source: SmartScreenDebug.evtx
{"EventData":{"Data":{"@Name":"Data","#text":"{\"$type\":\"isFileSupported\",\"executionTime\":\"3675\",\"path\":\"C:\\\\Users\\\\Dutch\\\\AppData\\\\Local\\\\MEGAsync\\\\MEGAsync.exe\",\"size\":\"77568264\"}"}}}
```

{{< admonition type=success title="FLAG" open=false >}}
MEGAsync
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: When was this utility executed?

The timestamp can be found in the log displayed in Task 7.

{{< admonition type=success title="FLAG" open=false >}}
2025–01–24 10:22:19
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: The Attacker also proceeded to destroy the data on the host so it is unrecoverable. What utility was used to achieve this?

Following the exfiltration with MEGAsync, another software was installed: [**File Shredder**](https://www.fileshredder.org/). It is describe by their website as a tool that _remove files from your hard drive without fear they could be recovered_.

```json
{"EventData":{"Data":{"@Name":"Data","#text":"{\"$type\":\"isFileSupported\",\"executionTime\":\"7943\",\"path\":\"C:\\\\Users\\\\Dutch\\\\Downloads\\\\file_shredder_setup.exe\",\"size\":\"2317839\"}"}}}
```

{{< admonition type=success title="FLAG" open=false >}}
File Shredder
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: The attacker cleared 2 important logs, thinking they covered all their tracks. When was the security log cleared?

Here we can run chainsaw to generate the _log_tampering.csv_ file. However, it’s a bit overkill and nothing a CTRL+F cannot achieve.

{{< image src="images/Screenshot_showing_log_tampering_by_the__7358.png" alt="Screenshot showing log tampering by the attacker (source: Security.evtx)" caption="Log tampering by the attacker (source: Security.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025–01–24 10:28:41
{{< /admonition >}}

---

This challenge was a little too easy because we were being guided through it. Also, the traces were almost all located in the same place (SmartScreenDebug). I was able to understand the importance of these event logs, but it became redundant as the questions progressed. I hope you were able to better understand the content of this Sherlock with my write-up.

_NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content._

{{< image src="images/SmartyPants_success_banner_5692.png" alt="SmartyPants success banner" caption="SmartyPants success banner" >}}
