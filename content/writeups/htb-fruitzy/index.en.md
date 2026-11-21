---
title: "HTB DFIR Sherlock: Fruitzy"
type: "posts"
author: WildPasta
author_url: "https://medium.com/@wildpasta"
published: 2026-05-02
source: Medium
draft: false
toc: false
categories: ["writeups"]
tags: ["hackthebox", "dfir", "writeups"]
---

### HTB DFIR Sherlock: Fruitzy

What could go wrong when someone click a random hyperlink in a phishing email? You will discover the whole initial access procedure with this Sherlock challenge. Topics covered in this WU: Edge History files, EVTX analysis and Threat Hunting.

---

> Task 1: What is the Subject/topic of the Phishing email?

After unzipping the archive, you can take a look at the `.eml` file given as the challenge input. Once opened up, you can see the Subject of the email.

{{< image src="images/Phishing_email__source__provided__eml_fi_6351.png" alt="Phishing email (source: provided .eml file)" caption="Phishing email (source: provided .eml file)" >}}

{{< admonition type=success title="FLAG" open=false >}}
Special Party Invitation from JANET CARNAHAN
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 2: What is the malicious URI that the malicious link redirected to?

You have to browse the Edge History database in `%localappdata%\microsoft\edge\user data\default` to find out the URL opened by the user when he clicked the link. 

The `downloads` table has only one entry that is our malicious file. The `tab_url` is our malicious URI and the `tab_referrer_url` is the cloudflare token protected URL embedded in the phishing email.

{{< image src="images/Browsing_history_of_the_user__source__Ed_967.png" alt="Browsing history of the user (source: Edge History)" caption="Browsing history of the user (source: Edge History)" >}}

{{< admonition type=success title="FLAG" open=false >}}
https://pomi.digital/premium/windows_download.php
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 3: What is the name of the downloaded file?

Still in the same `downloads` table, you can check out the `target_path` that indicate where the file was downloaded on disk.

{{< image src="images/Browsing_history_of_the_user__source__Ed_8342.png" alt="Browsing history of the user (source: Edge History)" caption="Browsing history of the user (source: Edge History)" >}}

{{< admonition type=success title="FLAG" open=false >}}
premium.exe
{{< /admonition >}}

```powershell
([DateTime]'1601-01-01').AddMilliseconds(13417116240329028 / 1000)
#output: 4 march 2026 16:44:00
```

{{< style "height:2rem;" >}}{{< /style >}}
> Task 4: When was the downloaded file executed by the victim according to Amcache?

Loading up `C:\Windows\AppCompat\Programs\Amcache.hve` you can find in the *Amcache_UnassociatedFileEntries.csv* the timestamp execution of `premium.exe`.

{{< image src="images/Execution_timestamp_of_the_malicious_PE__4200.png" alt="Execution timestamp of the malicious PE (source: AmCache.hve)" caption="Execution timestamp of the malicious PE (source: AmCache.hve)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2026-03-04 16:44:33
{{< /admonition >}}

{{< admonition type=tip title="Extra mile" open=true >}}
This can also be found in the Prefetch database.
{{< /admonition >}}

{{< image src="images/Execution_timestamp_of_the_malicious_PE__1478.png" alt="Execution timestamp of the malicious PE (source: C:\Windows\prefetch\)" caption="Execution timestamp of the malicious PE (source: C:\Windows\prefetch\)" >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 5: What is the SHA256 hash of the malicious executable downloaded from the phishing Website?

In the `downloads_url_chains` tab of the IE History database, you can find the download URI without the cloudflare protection enabled. Just download the file and SHA256 it to get the flag.

{{< image src="images/Download_link_of_the_RMM_executable__sou_5972.png" alt="Download link of the RMM executable (source: Edge History)" caption="Download link of the RMM executable (source: Edge History)" >}}

{{< admonition type=success title="FLAG" open=false >}}
af240a2c2a4b42e3a130f47ccaab9aa2e20a1a586bc959ee9efd7475055ea7e3
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 6: The user executed the file, but no invitation appeared or was found. They then used Microsoft Defender to scan the file. When was this scan initiated?

Once the EVTX are loaded up in Timeline Explorer, you can filter on the Defender provider to see its actions. Knowing that the compromised was after 16:44:00 (cf. Task 3) you can start your search from here.

{{< image src="images/Defender_scan_timestamp__source__Defende_138.png" alt="Defender scan timestamp (source: DefenderOperational.evtx)" caption="Defender scan timestamp (source: DefenderOperational.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2026-03-04 16:48:00
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 7: The malware installed a Remote Monitoring and Management (RMM) tool as a backdoor for potential remote access. What was the service name?

Let's search for an installed service after 16:44:00… There is one **very suspicious** that is most likely the intruder backdoor.

{{< image src="images/CentraStage_service_installation__source_3722.png" alt="CentraStage service installation (source :System.evtx)" caption="CentraStage service installation (source :System.evtx)" >}}

{{< admonition type=success title="FLAG" open=false >}}
CentraStage
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 8: The malicious backdoor installation time stomped the RMM executables. What was the modified timestamp set to these executables?

There is multiple RMM tools available online, you can easily find a list but here are some results and their executables location:

- Datto RMM (CentraStage): `C:\Program Files (x86)\CentraStage` or `C:\ProgramData\CentraStage`
- NinjaRMM: `C:\Program Files*\NinjaRMMAgent` or `C:\ProgramData\NinjaRMMAgent`
- ConnectWise: `C:\Program Files*\ConnectWise\*` or `C:\Program Files*\ScreenConnect\Bin`
- GoTo (LogMeIn): `C:\Program Files*\GoToMeeting\*` or `C:\Program Files*\GoToAssist\*`

In this case, it's the **CentraStage RMM** that is used. The modified timestamp can be located by checking the MFT record about `C:\Program Files (x86)\CentraStage\CagService.exe`.

{{< image src="images/Modified_timestamp_of_CagService_exe__so_3506.png" alt="Modified timestamp of CagService.exe (source: $MFT)" caption="Modified timestamp of CagService.exe (source: $MFT)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2026-02-09 07:56:40
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 9: What is the name of the company whose product is the RMM tool?

On Task 8, I found that the software editor of CentraStage was Datto.

{{< admonition type=success title="FLAG" open=false >}}
Datto
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 10: Pivoting back to the malicious link, when was the domain registered?

You can use DNS registration checker for this one. 

I personally went with https://lookup.icann.org/en/lookup

{{< image src="images/Malicious_domain_registration_timestamp__932.png" alt="Malicious domain registration timestamp (source: lookup icann)" caption="Malicious domain registration timestamp (source: lookup icann)" >}}

{{< admonition type=success title="FLAG" open=false >}}
2026-02-20 01:06:05
{{< /admonition >}}

{{< style "height:2rem;" >}}{{< /style >}}
> Task 11: Utilizing threat intelligence sources, what is another name for the executable that was initially downloaded?

By giving the SHA256 retrieved on Task 5 to [VirusTotal](https://www.virustotal.com/gui/file/af240a2c2a4b42e3a130f47ccaab9aa2e20a1a586bc959ee9efd7475055ea7e3/details) you can see in the *details* tab the other name of the file that were found in the wild.

{{< image src="images/Alternative_name_of_premium_exe__source__986.png" alt="Alternative name of premium.exe (source: VirusTotal)" caption="Alternative name of premium.exe (source: VirusTotal)" >}}

{{< admonition type=success title="FLAG" open=false >}}
5bxrx.exe
{{< /admonition >}}

---

This was a quick box fun to solve. I regret not having a deeper analysis of the compromission but the Threat Hunting part was kind of new to me here.

*NB: My write-up are written by myself, without any AI assistance. Excuse my poor english, I chose to share raw content.*

{{< image src="images/Fruitzy_success_banner_7014.png" alt="Fruitzy success banner" caption="Fruitzy success banner" >}}
