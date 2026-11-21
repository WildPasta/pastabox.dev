---
title: "HTB DFIR Sherlock: CAMouflage"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-09-06
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

# HTB DFIR Sherlock: CAMouflage

This Sherlock box displays real world TTPs to compromised the host and bypass AV detection.
On the forensic side you will dig through traditional prefetch but you will also learn about Windows BAM.

{{< admonition type=quote title="Initial statement" open=true >}}
A newly launched campaign has been detected targeting multiple users utilizing cracked applications. We received an alert indicating unusual behavior from one of our user’s laptops and performed an initial triage. Your task is to conduct a deep dive investigation to determine the root cause and extent of the incident.
{{< /admonition >}}

---

> Task 1: Based on forensic artifacts, at what precise timestamp did the user first execute the Cracked App installer?

There is no user folder available in the dump file so we cannot find the executable itself.
However, after browsing the prefetch database, you can identify a suspicious executable named *DOWNLOAD MASTERCAM X9 FULL CR*.

{{< admonition type=info title="How to parse prefetch from dump" open=true >}}
```powershell
PECmd -d "C:\Users\HTB\Desktop\camouflage\C\Windows\prefetch" `
      --csv "C:\Users\HTB\Desktop\camouflage\"
```
{{< /admonition >}}

The best indicator this artifact provides is an execution timestamp of every binary ran on the system.
By looking thoroughly we can find the one of the malicious installer.

{{< image src="images/prefetch_first_execution.png" alt="Prefetch showing the first execution of the malicious installer" caption="Prefetch showing the first execution of the malicious installer" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025-06-21 18:34:19
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
You can learn more about the executable by looking at the UserAssist artifact (located in *\Software\Microsoft\Windows\CurrentVersion\Explorer\UserAssist\\*)

{{< image src="images/user_assist_crack_execution.png" alt="Execution count and name of the malicious setup.exe" caption="Execution count and name of the malicious setup.exe" >}}
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: When did the installer process terminate?

The BAM (*Background Activity Moderator*) is a Windows service that tracks activity of background applications.
It was originally designed to improve battery life and system efficiency.

Let's parse this artifact to find more information about the Mastercam Crack.
The correct registry key to load is `SYSTEM\ControlSet001\Services\bam\State\UserSettings\{SID}`.
Here our user SID is `S-1-5-21-1403634729-3147206146-238420168-500`.

{{< image src="images/bam_artifact.png" alt="Execution timestamp found in BAM hive" caption="Execution timestamp found in BAM hive" >}}

{{< admonition type=info title="BAM caveat" open=true >}}
It is worth knowing that only locally executed binaries are registered in BAM artifact.
So if you load remotely an executable (from a SMB share for example), it will not be found there.
Also the entries expire after seven days if the program is inactive.
{{< /admonition >}}

{{< admonition type=success title="FLAG" open=false >}}
2025-06-21 18:36:52
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: What was the first file dropped by the malware post-installation?

The first execution timestamp is known, so you have to browse the `$MFT` with that in mind and look for any suspicious file dropped on disk.
Right after the installer launch (18:34:19), a suspicious file was written on disk at `2025-06-21 18:34:25.5115865`.
It is the one we are after!

{{< image src="images/mft_extracted_file_found.png" alt="Snippet of the MFT following the malicious setup execution" caption="Snippet of the MFT following the malicious setup execution" >}}

Notice that **the prefetch artifact is written after the execution** of the binary.
That's why it appears at the bottom of our screenshot, following the *Mastercam_Crack* start.

{{< admonition type=success title="FLAG" open=false >}}
Mysql.wp5
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: What is the SHA-256 hash of the .cab archive extracted during execution?

The `.cab` extension is a **Microsoft compressed archive** format (Cabinet) used in variety of Microsoft installation technologies.
From the previous task, you can see that the weird `*.wp5` files were written to `%TEMP%` directory.

You have to browse the folder where the files were extracted and execute `file` command on the `*.wp5` extension to find out the cab format:

```powershell
# powershell wrapper to iterate through the files
Get-ChildItem *.wp5 | ForEach-Object { file $_.FullName }

#output
[SNIP]C\Users\Administrator\AppData\Local\Temp\Art.wp5: data
[SNIP]C\Users\Administrator\AppData\Local\Temp\Authorization.wp5: data
[SNIP]C\Users\Administrator\AppData\Local\Temp\Gba.wp5: data
[SNIP]C\Users\Administrator\AppData\Local\Temp\Lock.wp5: data
[SNIP]C\Users\Administrator\AppData\Local\Temp\Mysql.wp5: ASCII text, with very long lines, with CRLF line terminators
[SNIP]C\Users\Administrator\AppData\Local\Temp\Play.wp5: Microsoft Cabinet archive data, 488221 bytes, 11 files
[SNIP]C\Users\Administrator\AppData\Local\Temp\Refugees.wp5: data
[SNIP]C\Users\Administrator\AppData\Local\Temp\Romania.wp5: data
[SNIP]C\Users\Administrator\AppData\Local\Temp\Runner.wp5: data
```

Bingo, you can see that `Play.wp5` is identified as a Cabinet Archive.
Then you have to `sha256sum` the file in order to get the flag!

{{< admonition type=success title="FLAG" open=false >}}
35efc15a41cf54a51703711e0b117b1899e4698bed1a4fdae638ebb7a3a190e0
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: What command did the malware use to extract content files from that .cab file?

Here you have to play around with **strings substitution** to understand what the batch script is doing.
So either you ask your favorite ChatBot to do the work for you and write a clumsy decoder OR you can **detonate the payload** in a sandbox like a chad.

I chose violence and ran it in my FlareVM and monitored the process spawned during the execution using Process Monitor.

The tool **extrac32** is used to achieve the extraction.

{{< image src="images/payload_extraction.png" alt="Payload extraction using extrac32" caption="Payload extraction using extrac32" >}}

{{< admonition type=success title="FLAG" open=false >}}
extrac32 /Y Play.wp5 \*.\*
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: During execution, the malware performed AV/EDR checks. How many security product-related strings did it search for in memory or processes?

Same process as in previous task, I filtered out the `Command line` keyword in the details column and found the AV check.

{{< image src="images/edr_scanner.png" alt="Antivirus process scanned by the payload" caption="Antivirus process scanned by the payload" >}}

Additional information about the scanned services:

| Process Name  | Vendor - Coponent     | Usual Binary Path                                                    |
|---------------|-----------------------|----------------------------------------------------------------------|
| bdservicehost | Bitdefender           | C:\Program Files\Bitdefender\Bitdefender Security\bdservicehost.exe  |
| SophosHealth  | Sophos Health Service | C:\Program Files\Sophos\Endpoint Defense\SED_ML\SophosHealth.exe     |
| AvastUI       | Avast Antivirus UI    | C:\Program Files\Avast Software\Avast\AvastUI.exe                    |
| AVGUI         | AVG AntiVirus UI      | C:\Program Files\AVG\Antivirus\AVGUI.exe                             |
| nsWscSvc      | Norton Security       | C:\Program Files (x86)\Norton Security\Engine\\*\nsWscSvc.exe        |
| ekrn          | ESET Kernel Service   | C:\Program Files\ESET\ESET Security\ekrn.exe                         |

{{< admonition type=success title="FLAG" open=false >}}
6
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: After the batch file was executed, what was the name of the process that ran?

So we know that the batch file ultimately ran a command extracting the `.cab` archive by calling `extrac32.exe`.
You have more that enough information to guess that it will end up in the prefetch database, shortly after an entry looking like `[FOO]\WINDOWS\SYSWOW64\EXTRAC32.EXE`

{{< image src="images/execution_moscow_prefetch.png" alt="Payload start after Cabinet archive extraction" caption="Payload start after Cabinet archive extraction" >}}

{{< admonition type=success title="FLAG" open=false >}}
MOSCOW.COM
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: What is the original name for that process?

There are multiple solution to solve this task.
I'm going to show you some of them to trace back the origin of the payload.

First of all, in the strings you end up finding references to AutoIt domain.

{{< image src="images/autoit_string_moscow.png" alt="Interesting strings found in MOSCOW.COM.exe" caption="Interesting strings found in MOSCOW.COM.exe" >}}

Then by right-clicking and showing description, you can find more clues about its origin.

{{< image src="images/autoit_description_moscow.png" alt="MOSCOW.COM.exe description in File Explorer" caption="MOSCOW.COM.exe description in File Explorer" >}}

If you were yet unsure about the binary name, you could try to submit its hash into [VirusTotal](https://www.virustotal.com/gui/file/1300262a9d6bb6fcbefc0d299cce194435790e70b9c7b4a651e202e90a32fd49/relations).

{{< image src="images/autoit_vt_moscow.png" alt="Submitting MOSCOW.COM hash to VirusTotal" caption="Submitting MOSCOW.COM hash to VirusTotal" >}}

But maybeee if it's still not enough proof, you can deobfuscate the `.bat` script to find out the following.

{{< image src="images/autoit_deobf_moscow.png" alt="String substitution from MOSCOW.COM to AutoIt3.exe" caption="String substitution from MOSCOW.COM to AutoIt3.exe" >}}

{{< admonition type=success title="FLAG" open=false >}}
AutoIt3.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: What is the SHA-256 hash of the file loaded by the above identified process?

By running my clunky deobfuscation script, I managed to retrieve partial information about the file built by the stager.
It concatenates the previously extracted files (`wp5` extension) into one binary to recreate it in order to bypass EDR detection. 

```powershell
# line 346 of Mysql.wp5
copy /b ..\Runner.wp5 + ..\Art.wp5 + ..\Gba.wp5 + ..\Romania.wp5 + ..\Refugees.wp5 + ..\Authorization.wp5 + ..\Lock.wp5 K.a3x
```

The temporary `K` file was deleted but we know the workflow to craft it back!
So let's get to work:

```powershell
copy /b ..\Runner.wp5 + ..\Art.wp5 + ..\Gba.wp5 + ..\Romania.wp5 ^
      + ..\Refugees.wp5 + ..\Authorization.wp5 + ..\Lock.wp5 K.a3x
# output of the command
..\Runner.wp5
..\Art.wp5
..\Gba.wp5
..\Romania.wp5
..\Refugees.wp5
..\Authorization.wp5
..\Lock.wp5
        1 file copied.
```

Now you just have to hash the file to get the flag.

```powershell
PS> Get-FileHash .\K.a3x -Algorithm SHA256 | Format-List
Algorithm : SHA256
Hash      : 2B3D1561B9AE7FA2BD3F09DEE28A327B5647A908113945CD2A943134822D18D0
Path      : [SNIP]\C\Users\Administrator\AppData\Local\Temp\448887\K
```

{{< admonition type=success title="FLAG" open=false >}}
2B3D1561B9AE7FA2BD3F09DEE28A327B5647A908113945CD2A943134822D18D0
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: What is the C2 Domain name address contacted by the malware?

For this question you have to submit the previously computed SHA256 hash to [VirusTotal](https://www.virustotal.com/gui/file/2b3d1561b9ae7fa2bd3f09dee28a327b5647a908113945cd2a943134822d18d0).
Switching to the community tab, we can learn thanks to *noobbot* that the infection chains ultimately connects back to `crowfza.xyz`.

{{< image src="images/virustotal_comment_tab.png" alt="Comment showing the C2 used by the malware" caption="Comment showing the C2 used by the malware" >}}

{{< admonition type=success title="FLAG" open=false >}}
crowfza.xyz
{{< /admonition >}}

--- 

That was a quick box to solve but I still took time to find out about the BAM artifact.
Nice workflow of real world TTPs!

*NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content.*

{{< image src="images/success_banner_camouflage.png" alt="CAMouflage success banner" caption="CAMouflage success banner" >}}