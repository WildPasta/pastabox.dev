---
title: "[EN] HTB DFIR Sherlock: WorkFromHome"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-03-08
source: Medium
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

# HTB DFIR Sherlock: WorkFromHome

Today I dive into another windows forensic investigation. Here a user was deceived by a malicious website and gave the attacker its credentials. Then, the intruder compromised the host by elevating its privilege through PrintConfig and established persistence by hijacking a WMI workflow. This was no easy task due to the number of questions, but definitely easier than EasyMoney.

---

> Task 1: Identify the phishing URL that the user clicked on, resulting in credential harvesting.

It is likely that a web browser was used to click the malicious URL. So let’s browse through chrome database `%localappdata%\google\chrome\user data\default` as we did in the write-up on Shadowbait.

In the `History` file, you can find a lot of connections to `wowzainc.co.th` which is the internal domain of Wowza Enterprise. Howeveeer, an email title called _Important update_ should trigger your attention. 

Following the URL IDs, you can notice that the user goes from a `mail.wowzainc.co.th` to a `login.wozaln.co.th` (see the **typosquatting** here?).

{{< image src="images/Chrome_browsing_history_showcasing_typos_7422.png" alt="Chrome browsing history showcasing typosquatting" caption="Chrome browsing history showcasing typosquatting" >}}

{{< admonition type=success title="FLAG" open=false >}}
http://login.wowzalnc.co.th/logon.php
{{< /admonition >}}

You can also note down the timestamp to have an initial compromission starting point.

```powershell
([DateTime]'1601-01-01').AddMilliseconds(13392643002023957 / 1000)
#output: 25 may 2025 10:36:42
```

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: When did the threat actor gain access to the victim’s computer via RDP for the first time?

The RDP connection log is located in LocalSessionManager. We got a first RDP login at 09:23:08 on the 2025–05–25. It must be the legitimate user because it’s `otello.j` that uses RDP locally. But after that, a RDP connection comes from IP **192.168.189.129**, which is not localhost obviously (otherwise it would have been mentioned `local`🤓).

{{< image src="images/First_RDP_connection_with_external_IP__s_7212.png" alt="First RDP connection with external IP (source: LocalSessionManager.evtx)" caption="First RDP connection with external IP (source: LocalSessionManager.evtx)" >}}

The session arbitration means that the RDP authentication was successful but the provider still has to figure out what to do with the incoming connection: is a user already connected? which session id to assign?

We also got our first IOC: the attacker’s IP address on the local network.

{{< admonition type=success title="FLAG" open=false >}}
2025–05–27 11:59:57
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
Out of habit I go through logs before and after the wanted one. And here we can see that a NT Hash logon (LogonType 3) was successful at 11:59:36 from a host named kali with our attacker’s IP! So the credentials were likely tested against SMB or WMI first before connecting through RDP.
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: The threat actor accessed several sensitive files on the victim’s work-related folder. What is the full path of the PowerPoint presentation file opened by the attacker?

For this question, there is two way of solving. The quicker one is to search the whole MFT for a `.pptx` extension and filters out on our compromised `otello.j`.

Or you could be more thorough in the analysis and think that since the attacker used RDP to login, he should have used GUI to open-up the Powerpoint file. And this kind of artifacts is reference in `UserAssist` hive or in `JumpList` artifacts!

{{< image src="images/Documents_opened_by_the_intruder__source_4628.png" alt="Documents opened by the intruder (source: JumpList)" caption="Documents opened by the intruder (source: JumpList)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\otello.j\Desktop\Working\Proposal to CFO.pptx
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: The threat actor discovered a privilege that allows specific volume-level management operations and could be exploited to get full control over the C drive. What is this special privilege?

Actually, you can see the PrivilegeList assigned to users when they log-in by browsing event 4672 (special privileges assigned), but I couldn’t find the one I was looking for in the Secutiry EVTX… So I had to guess over the question formulation.

{{< admonition type=success title="FLAG" open=false >}}
SeManageVolumePrivilege
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: What is the name of the executable downloaded by the threat actor to exploit previously found privilege?

You have to browse the `downloads` tab of **Chrome history** to find out that a file called **SeManageVolumeExploit** was downloaded at 12:43:33 on the 28th of May.

{{< image src="images/SeManageVolumeExploit_download_location__7198.png" alt="SeManageVolumeExploitdownload location (source: Chrome History)" caption="SeManageVolumeExploitdownload location (source: Chrome History)" >}}

It is a [well known exploit](https://github.com/CsEnox/SeManageVolumeExploit) to **LPE on a windows system**. The readme show how to achieve SYSTEM shell access by dropping a malicious printconfig.dll in `C:\windows\system32\spool\drivers\x64\3` that leads to a **DLL side-loading** attack (MITRE [T1574.002](https://attack.cloudfall.cn/techniques/T1574/002/)).

{{< admonition type=success title="FLAG" open=false >}}
SeManageVolumeExploit.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: What is the full URL from where the threat actor tried to download a DLL file?

Still in the same database, the **second requirements for SeManageVolume Exploit** was downloaded short after the first executable.

{{< image src="images/PrintConfig_download_source__source__Chr_7105.png" alt="PrintConfig download source (source: Chrome History)" caption="PrintConfig download source (source: Chrome History)" >}}

{{< admonition type=success title="FLAG" open=false >}}
http://freehackingtool.com/tools/PrintConfig.dll
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: The malicious DLL file was not successfully downloaded, as the download was interrupted by the safe browsing safety feature. Research Browser forensics and find the description of the interrupt reason that caused the download to be disrupted.

This question was a fun one I never came across in my browser forensic experience. In the `downloads` tab of our Chrome database, there is a column named `danger_type` and another named `interrupt_reason`. Next to our _PrintConfig.dll_, these values are non-zero.

{{< image src="images/Download_interrupt_reason__source__Chrom_6511.png" alt="Download interrupt reason (source: Chrome History)" caption="Download interrupt reason (source: Chrome History)" >}}

To understand what these value represent, you can review [this article](https://dfir.blog/chrome-values-lookup-tables/) that directly bind the source code of chromium with the error type. You can find either [danger type](https://source.chromium.org/chromium/chromium/src/+/main:components/download/public/common/download_danger_type.h) and [interruption values](https://source.chromium.org/chromium/chromium/src/+/main:components/download/public/common/download_interrupt_reason_values.h) on it (S/O Ryan Benson).

{{< image src="images/Interrupt_reason_ID_41__source__chromium_5658.png" alt="Interrupt reason ID 41 (source: chromium source code)" caption="Interrupt reason ID 41 (source: chromium source code)" >}}

In our case, _interrupt_code_41 is for a closed browser during the download. Also, _danger_type_7 warns about a **dangerous host** (known to serve mostly malicious content).

{{< admonition type=success title="FLAG" open=false >}}
The user shut down the browser
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: Since the download was not successful from the browser directly, which LOLBIN did the threat actor use to download this file successfully?

I couldn’t find any evidence in the logs but was 99% sure that _certutil_ was used since it’s a [common LOLBIN](https://lolbas-project.github.io/lolbas/Binaries/Certutil/#download) used for download. To confirm our theory, let’s check certutil cache folder (that we used in our [EasyMoney WU]({{< ref "../htb-easymoney/index.en.md" >}})). Simply `strings *` in the _MetaData_ folder.

{{< image src="images/Malicious_DLL_found_in_certutil_exe_cach_1137.png" alt="Malicious DLL found in certutil.exe cache folder" caption="Malicious DLL found in certutil.exe cache folder" >}}

Since we have the content of our malicious dll logged here, it means that we were correct! Still I find it strange that it wasn’t even logged in the prefetch artifacts 🤔.

{{< admonition type=success title="FLAG" open=false >}}
certutil.exe
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: When was the malicious DLL file successfully downloaded using this LOLBIN?

So here comes a trap, you would be tempted to look in the MFT for our dear `PrintConfig.dll`. However, there is no result for this entry! But if you query **UsnJrnl**, you will find a **FileCreate entry** in it for our file 🤯.

{{< image src="images/Trace_of_malicious_PrintConfig_dll_downl_5556.png" alt="Trace of malicious PrintConfig.dll download (source: $UsnJrnl)" caption="Trace of malicious PrintConfig.dll download (source: $UsnJrnl)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025–05–28 12:45:37
{{< /admonition >}}

But how could a file be present in UsnJrnl and not in MFT? You have to understand that the **MFT is a static table** - see it as a phone book - from which the **entries can be overwritten** if the referenced file is deleted. So if our _PrintConfig.dll_ was ran then deleted right after, there is a high probability where the entry was replaced by another file reference. It reflects the **current filesystem state** and scale with file count.

However, the **UsnJrnl is a changelog** of every filesystem operation - see it as a call log - that stores file creation, rename, deletion… It’s a **circular buffer** of about ten MB that logs records until buffer wraps…

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: To gain System privileges, the threat actor replaced an existing DLL with the same name. What is the original path of the legitimate DLL?

If you keep looking in the **UsnJrnl**, you can see what happened to our malicious DLL. As shown on the screenshot below, a legitimate PrintConfig DLL got deleted then replaced by the one in Downloads folder (as per **RenameOldName** suggests). This flow looks a looot like the one described in the exploit from Task 5.

{{< image src="images/Trace_of_legitimate_PrintConfig_dll_dele_6394.png" alt="Trace of legitimate PrintConfig.dll deletion (source: $UsnJrnl)" caption="Trace of legitimate PrintConfig.dll deletion (source: $UsnJrnl)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Windows\System32\spool\drivers\x64\3\Printconfig.dll
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 11: The threat actor removed the legitimate DLL before replacing it with the malicious DLL. When was the legit DLL deleted?

You can find this piece of information on the screenshot in Task 10. It shows a FileDelete operation in the UsnJrnl that affected the legitimate PrintConfig.dll at: **2025–05–28 12:47:06**

{{< admonition type=success title="FLAG" open=false >}}
2025–05–28 12:47:06
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 12: When was the malicious DLL detected as malware?

This information is located in the Windows Defender EVTX with the _Detection_ keyword. So let’s filter Timeline Explorer on that and see the results.

{{< image src="images/PrintConfig_dll_detection_by_Defender__s_6812.png" alt="PrintConfig.dll detection by Defender (source: WindowsDefender.evtx)" caption="PrintConfig.dll detection by Defender (source: WindowsDefender.evtx)" >}}

Detection of the malicious _PrintConfig.dll_ file was on: **2025–05–28 15:19:35**

{{< admonition type=success title="FLAG" open=false >}}
2025–05–28 15:19:35
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 13: The threat actor initiated a Windows component to load this DLL. What is the CLSID of this component?

You have to browse in otello’s **Powershell history** in order to find commands typed by the intruder. And we can read out the wanted CLSID there.

```powershell
#source: c:\users\otello.j\appdata\Microsoft\Windows\Powershell\PSReadline\ConsoleHost_history.txt
dir
$type = [Type]::GetTypeFromCLSID("{854A20FB-2D44-457D-992F-EF13785D2B51}")
$object = [Activator]::CreateInstance($type)
dir
reg add "HKCU\control panel\desktop" /v wallpaper /t REG_SZ /d "C:/Users/Public/Pictures/gg.bmp" /f
```

We also notice there a weird `reg add` command that will be used later on in the investigation 🕵️‍♂️.

{{< admonition type=success title="FLAG" open=false >}}
{854A20FB-2D44–457D-992F-EF13785D2B51}
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 14: What is the name of the service/object associated with this CLSID?

This task can be answer either by analyzing the logs or looking online:

- In the Executable Info field of our Detection (Task 12), in the full output, you can read the service attributed to the malicious DLL: PrintNotify (remove the leading underscore)

{{< image src="images/PrintNotify_service_identification__sour_8400.png" alt="PrintNotify service identification (source: WindowsDefender.evtx)" caption="PrintNotify service identification (source: WindowsDefender.evtx)" >}}

- Or you could have googled the found CLSID and see that it is bound to the PrintNotify local service (example on Juicy Potato Git)

{{< image src="images/CLSID_of_PrintNotify_from_known_CLSID_da_565.png" alt="CLSID of PrintNotify from known CLSID database (source: Juicy Potato Git)" caption="CLSID of PrintNotify from known CLSID database (source: Juicy Potato Git)" >}}

{{< admonition type=success title="FLAG" open=false >}}
PrintNotify
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 15: What is the SHA1 hash of the malicious DLL file?

When a suspicious file is dropped on disk, it’s interceppted by windows **minifilter driver**. Then it runs a scan and logs its result in `C:\ProgramData\Microsoft\Windows Defender\Support`. In this case, since _PrintConfig.dll_ was **spotted by Defender**, you can see the SHA1 in its analysis.

{{< image src="images/Defender_analysis_of_PrintConfig_dll__so_5315.png" alt="Defender analysis of PrintConfig.dll (source: MPLog-20250528–145950.log)" caption="Defender analysis of PrintConfig.dll (source: MPLog-20250528–145950.log)" >}}

{{< admonition type=success title="FLAG" open=false >}}
916564984e38f8bb91921cd4e40b64156a72142b
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 16: A Second DLL file was downloaded from the same malicious domain. Where was it downloaded on the filesystem?

Filtering our **UsnJrnl entries** on dll extension and otello’s **downloads folder**, we find only one new DLL named `tzres.dll`.

{{< image src="images/Trace_of_tzres_dll_in__UsnJrnl_5040.png" alt="Trace of tzres.dll download (source: $UsnJrnl)" caption="Trace of tzres.dll download (source: $UsnJrnl)" >}}

But weirdly enough, the location doesn’t match HTB submission… Let’s filter out on tzres.dll but this time, **machine wide**. And now we see that another instance exists in `.\Windows\System32\wbem`. That’s the one we are looking for here!

{{< image src="images/Trace_of_tzres_dll_in__UsnJrnl_8696.png" alt="Trace of tzres.dll download in $UsnJrnl" caption="Trace of tzres.dll download in $UsnJrnl" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\windows\system32\wbem\tzres.dll
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 17: When was this DLL downloaded on the system?

Timestamp is the one screenshoted above 🙄

{{< admonition type=success title="FLAG" open=false >}}
2025–05–28 12:54:23
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 18: The threat actor downloaded a VBScript for command execution to facilitate the DLL execution of the second malicious DLL. What is the full path of this script after it was moved to a new location?

Going back to our **UsnJrnl log file**, we search for any `.vbs` file that hit the host disk.

{{< image src="images/Hunting_for_malicious_VBScript_4598.png" alt="Hunting for malicious VBScript" caption="Hunting for malicious VBScript" >}}

We find the suspicious `a.vbs` that was downloaded in otello’s downloads folder before beeing moved to **StartUp folder**. Windows uses this folder every time a user logs in and run whatever is inside it. It’s a very easy **persistence method**: no registry, no admin right and survive reboot).

{{< admonition type=success title="FLAG" open=false >}}
C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp\a.vbs
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 19: What is the full command that the script is configured to execute?

So the VBScript download location is known (Task 18) and was apparently collected by KAPE. You can find its content below.

```powershell
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "cmd.exe /c systeminfo", 0, False
```

{{< admonition type=success title="FLAG" open=false >}}
cmd.exe /c systeminfo
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 20: The threat actor configured the VBS script to be hidden from the Windows GUI (File Explorer). When was this attribute set on the file?

In the **UsnJrnl**, the script was a basic archive (automatically labeled by windows) but THEN got a **Hidden attribute**. This file property hide the corresponding file from the GUI but still can be shown by typing `dir /a:h`.

{{< image src="images/Adding_Hidden_attribute_to_the_malicious_8339.png" alt="Adding Hidden attribute to the malicious script" caption="Adding Hidden attribute to the malicious script" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025–05–28 12:56:11
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 21: Which process loads the previously identified DLL with this command? The command executed by the VBS script ultimately facilitates loading and execution of the Second malicious DLL, providing persistence and execution capabilities to the attacker.

So basically, `systeminfo` is just a display tool that doesn’t do its own data collection. It asks WMI for all the system information.

Here the attack works because `wmiprvse.exe` lives in `System32\wbem` and the legitimate `tzres.dll` is located in `System32`. The DLL search order look up through the executable’s folder BEFORE looking up `System32` folder. This means that the malicious `tzres.dll` located in `wbem` is loaded BEFORE the one in `System32` and all that in `wmiprvse.exe` context. It’s a **execution flow hijacking** attack, more specifically a _search order hijacking_ (MITRE [T1574.001](https://attack.mitre.org/techniques/T1574/001/)).

{{< admonition type=success title="FLAG" open=false >}}
wmiprvse.exe
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
`tzres.dll` is the DLL used to get informations about the timezone. Nothing calls directly the malicious DLL, instead the legitimate chains **triggers it naturally**: vbs → cmd → systeminfo → WMI → wmiprvse.

It also echoes the initial note stating that systeminfo is crashing on some hosts. If the `tzres.dll` doesn’t export or proxy the functions used by `wmiprvse.exe` then it causes `wmiprvse` to crash, which in turn causes a crash of `systeminfo.exe`.
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 22: The threat actor downloaded an image file to change the desktop wallpaper. What is the full path of this file?

You can find the wallpaper picture name under `NTUSER.DAT\Control Panel\Desktop` registry key.

{{< image src="images/Wallpaper_source_found_in_NTUSER_DAT_reg_5408.png" alt="Wallpaper source found in NTUSER.DAT registry hive" caption="Wallpaper source found in NTUSER.DAT registry hive" >}}

Once this information is known, simply search through the $**UsnJrnl**for `gg.bmp `to find out its download location. It seems that it was the same as the source image from registry explorer.

{{< image src="images/Tracking_image_download_locations__sourc_5024.png" alt="Tracking image download locations (source: $UsnJrnl)" caption="Tracking image download locations (source: $UsnJrnl)" >}}

{{< admonition type=success title="FLAG" open=false >}}
C:\Users\Public\Pictures\gg.bmp
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 23: The threat actor then proceeded to change the desktop wallpaper of the compromised user to the newly downloaded image. Find the time when the wallpaper was altered?

Let’s remember what we discover on Task 13 (yes, it was a long time ago). A `reg add` command was used to change the user wallpaper! You can check when this was run by looking at PowershellOperational EVTX.

{{< image src="images/Command_used_to_change_victim_s_wallpape_8543.png" alt="Command used to change victim’s wallpaper (source: PowershellOperational.evtx)" caption="Command used to change victim’s wallpaper (source: PowershellOperational.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2025-05-28 12:59:30
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 24: When did the victim user log in to their workstation after the compromise?

We’re going to use the **same method as for Task 2** (where we searched for the attacker’s RDP connection) and open the **LocalSessionManager** provider event log. So, if you filter on event ID 41 (RDP session arbitration), you’ll see that **otello logged in locally**(as it should for the company) at 15:04:41.

{{< admonition type=success title="FLAG" open=false >}}
2025-05-28 15:04:41
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 25: What is the message on the new wallpaper?

In the **UsnJrnl** search, you can see that the `gg.bmp`was downloaded in **Pictures folder** but also in the certutil cache at **SYSTEM level**. That surely is odd because certutil is not supposed to be downloading files with that high-privilege.

{{< image src="images/Tracking_gg_bmp_locations__source___UsnJ_8740.png" alt="Tracking gg.bmp locations (source: $UsnJrnl)" caption="Tracking gg.bmp locations (source: $UsnJrnl)" >}}

And when you strings the _MetaData_ cache to check file sources, you find our `gg.tmp`!

{{< image src="images/Wallpaper_found_in_certutil_exe_cache_fo_113.png" alt="Wallpaper found in certutil.exe cache folder" caption="Wallpaper found in certutil.exe cache folder" >}}

You now have to open up this file but in the content folder to find the wallpaper changed by the attacker.

{{< image src="images/Hacked_by_anarchy_wallpaper_9061.png" alt="Wallpaper set by the intruder on otello’s desktop" caption="Wallpaper set by the intruder on otello’s desktop" >}}

{{< admonition type=success title="FLAG" open=false >}}
HACKED BY ANARCHY
{{< /admonition >}}

This was a fun box where I poked around the UsnJrnl and discovered a fun persistence used by the attacker (leveraging `systeminfo`). Overall, it was a nice box with lot of twists and events to be analyzed from multiple sources (Chrome, Defender, Security, certutil cache…).

_NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content._

{{< image src="images/WorkFromHome_success_banner_9703.png" alt="WorkFromHome success banner" caption="WorkFromHome success banner" >}}
