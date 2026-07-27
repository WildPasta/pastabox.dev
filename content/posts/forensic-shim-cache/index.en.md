---
title: "Windows Shimcache in forensic"
type: "posts"
author: WildPasta
published: 2024-04-02
description: "Short explanation about Windows Shimcache"
summary: ""
draft: false
categories: ["forensic", "windows"]
tags: ["artifact"]
---

## What is it?

Windows XP introduced a mechanism for better **application compatibility** between applications and Windows. This feature is officially known as `Application Compatibility`, but it's more commonly called `Application Shimming`.
How the `Shim Engine` works is explained in more detail in another post.

What matters for our analysis is that it uses an application cache to speed up requests to its database. [[1]](#references)
The **Shimcache** therefore contains the list of executables that have recently been queried by the **Shim Engine**.

A small but important detail: it's a cache with a **maximum of 1024 entries**, managed with the **FIFO method** (First-In, First-Out).

## Why it matters for forensics

Thanks to this feature, we can see every **application that has been seen on the OS**.
And the beautiful part is that even executables that don't need to go through the *shim* infrastructure still get added!

Alongside the file names, we also get the following information [[2][3]](#references):

- The **full path** of the executable, even if it's a UNC path or one on removable media
- Its **last modified date**, pulled from `$SI` (*Standard_Information*) in the `$MFT` — not to be confused with its date of addition to the `Shimcache`

{{< admonition type=tip title="About the MFT" open=false >}}
The **MFT** is a **database** that holds the list of files and directories on the system.
Its **$SI** field holds timestamp information for a file (creation, modification, last access).
This **information is written by the kernel**, not by the user, which makes it harder to tamper with.
{{< /admonition >}}

- Its **position in the cache** (the most recent entries appear first in the list)
- On *Windows XP* and *Windows 2003*, we also get the **file size** and the **cache update date**
- Between *Windows XP* and *Windows 8.1*, we get the **Exec Flag**, indicating whether it has already been run or not [[4]](#references)

Note that renaming or moving a file will **put it back in the Shimcache**.

A very interesting trace of an intrusion can be left when a file is created, and the attacker then performs **timestomping** on it.

{{< admonition type=warning title="Timestomping" open=true >}}
**Timestomping** is a technique used by attackers that consists of manipulating a file's timestamps to hide it among other, older files on the system.
The goal is typically to make an executable look legitimate.
{{< /admonition >}}

We can compare the last-modified dates in the `Shimcache` with those on the file system, and any discrepancy could reveal this evasion technique.
Indeed, the `Shimcache` can be trusted here, since it refers back to the **$SI field of the MFT**.

## Limitations of this artifact

Entries are only written to the `Shimcache` **when the machine reboots**, which can make analysis trickier during a forensic investigation.
That said, a Volatility module lets you view the Shimcache while it's still in RAM.

Files only get added to the `Shimcache` if they were seen through `explorer.exe` — not, for example, via a `dir` command in a terminal.

The **execution flag** can be added to the `Shimcache` when available, but **it can't be trusted** on recent Windows distributions (post-W8.1) [[4][5]](#references).
It's more useful to correlate it with other artifacts to confirm execution.

## It's dump time!

### AppCompatCacheParser

To dump the `Shimcache`, you can either start from a dump of the registry keys (with **FTK Imager**, for example), or dump the cache live.
As usual on Windows, we'll use a tool from the **Zimmerman suite**.

```powershell
.\AppCompatCacheParser.exe  --csv C:\Users\user\Desktop\
```

We can then parse the file with **Timeline Explorer**:

{{< image src="images/timeline_explorer_shimcache_dump.png" alt="Analyzing the dump with Timeline Explorer" caption="Analyzing the dump with Timeline Explorer" >}}

We do find the artifacts mentioned in the **"Why it matters for forensics"** section.

### Chainsaw

We can also parse the `Shimcache` with [Chainsaw from WithSecure](https://github.com/WithSecureLabs/chainsaw) [[6]](#references).
```powershell
.\chainsaw.exe analyse shimcache C:\Users\user\Desktop\system_hive --output shimcache.dmp
```

### Volatility

A volatility2 module also exists for reading the `Shimcache` directly from memory [[7][8]](#references).
If you've been following along, this plugin addresses exactly the limitation mentioned earlier, where the `Shimcache` lives in RAM until reboot, when it's finally written to disk.

```powershell
# On Windows XP we can see we have access to the file size
python vol.py -f D:\Projects\Volatility\WinXPSP2x86.bin --profile=WinXPSP2x86 --kdbg=0x8054cde0 --dtb=0x39000 shimcachemem
Volatility Foundation Volatility Framework 2.5

Order Last Modified         Last Update           Exec  File Size  File Path
----- --------------------- --------------------- ----- ---------- ---------
    1 2012-11-27 01:42:21   2012-11-27 01:57:28              95104 \??\C:\mdd.exe
    2 2008-04-14 11:42:06   2012-11-27 01:56:17            8461312 \??\C:\WINDOWS\system32\SHELL32.dll
    3 2008-04-14 11:42:40   2012-11-27 01:56:17              28672 \??\C:\WINDOWS\system32\verclsid.exe

# Comparing against W7 results taken from Andrea Fortuna's blog
$ vol.py -f win7.vmem --profile=Win7SP1x86 shimcache
Volatility Foundation Volatility Framework 2.4
Last Modified                  Path
------------------------------ ----
2009-07-14 01:14:22 UTC+0000   \??\C:\Windows\system32\LogonUI.exe
2009-07-14 01:14:18 UTC+0000   \??\C:\Windows\system32\DllHost.exe
2009-07-14 01:16:03 UTC+0000   \??\C:\Windows\System32\networkexplorer.dll
2009-07-14 01:14:31 UTC+0000   \??\C:\WINDOWS\SYSTEM32\RUNDLL32.EXE
2011-03-22 18:18:16 UTC+0000   \??\C:\Program Files\VMware\VMware Tools\TPAutoConnect.exe
2009-07-14 01:14:25 UTC+0000   \??\C:\Windows\System32\msdtc.exe
2009-07-14 01:15:22 UTC+0000   \??\C:\Windows\System32\gameux.dll
2011-08-12 00:00:18 UTC+0000   \??\C:\Program Files\Common Files\VMware\Drivers\vss\comreg.exe
2010-08-02 20:42:26 UTC+0000   \??\C:\Program Files\VMware\VMware Tools\TPAutoConnSvc.exe
2009-07-14 01:14:27 UTC+0000   \??\C:\Windows\system32\net1.exe
2009-07-14 01:14:27 UTC+0000   \??\C:\Windows\System32\net.exe
2011-08-12 00:06:50 UTC+0000   \??\C:\Program Files\VMware\VMware Tools\vmtoolsd.exe
2009-07-14 01:14:45 UTC+0000   \??\C:\Windows\system32\WFS.exe
```

## Conclusion

The `Shimcache` is a forensic artifact rich in information.
During an investigation, it's analyzed to **correlate** executables that are (or were) present on the system.
This artifact makes it harder for an attacker to **cover their tracks**.
On the other hand, it's harder to analyze when the machine can't be rebooted.

## References

- [1] [Demystifying Shims](https://techcommunity.microsoft.com/t5/ask-the-performance-team/demystifying-shims-or-using-the-app-compat-toolkit-to-make-your/ba-p/374947)

- [2] [The Value of Shimcache for Investigators](https://www.mandiant.com/resources/blog/caching-out-the-val)

- [3] [Let's Talk About Shimcache - 13Cubed](https://www.youtube.com/watch?v=7byz1dR_CLg)

- [4] [Shimcache for Forensic](https://artefacts.help/windows_shimcache.html)

- [5] [The (Mis)Use of Artifact Categories](https://windowsir.blogspot.com/2022/02/the-misuse-of-artifact-categories.html)

- [6] [Chainsaw for Shimcache](https://labs.withsecure.com/tools/chainsaw-analyse-shimcache)

- [7] [Andrea Fortuna Blog](https://andreafortuna.org/2017/07/31/volatility-my-own-cheatsheet-part-6-windows-registry/)

- [8] [Volatility Shimcache Module](https://github.com/mandiant/Volatility-Plugins/blob/master/shimcachemem/README.md)