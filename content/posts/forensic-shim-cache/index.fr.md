---
title: "Le Shimcache Windows en forensic"
type: "posts"
author: WildPasta
published: 2024-04-02
description: "Petite explication du shimcache"
summary: ""
draft: false
categories: ["forensic", "windows"]
tags: ["artifact"]
---

## Qu'est-ce que c'est ?

Windows XP a introduit un mécanisme qui permet d'avoir une meilleure **compatibilité applicative** entre les applications et Windows. Cette fonctionnalité est connue sous le nom d'`Application Compatibility` mais plus souvent appelée `Application Shimming`.
Le fonctionnement du `Shim Engine` est expliqué plus en détail dans un autre post.

Ce qu'il y a d'important à retenir pour notre analyse, c'est qu'il utilise un cache applicatif pour accélérer les requêtes vers sa base de données. [[1]](#references)
Le **Shimcache** contient donc la liste des exécutables qui ont été requêtés récemment par le **Shim Engine**.

Petite subtilité qui a son importance : c'est un cache de **1024 entrées maximum**, géré avec la **méthode FIFO** (First-In, First-Out).

## L'intérêt forensic

Grâce à cette fonctionnalité, on peut voir toutes **les applications qui ont été vues sur l'OS**.
Et ce qui est beau c'est que même les exécutables qui n'ont pas besoin de passer par l'infrastructure *shim* y sont ajoutés !

En plus des noms de fichiers, on récupère les informations suivantes [[2][3]](#references) :

- Le **chemin complet** de l'exécutable, même si c'est un chemin UNC ou celui d'un support amovible
- Sa **date de dernière modification** récupérée au niveau de `$SI` (*Standard_Information*) dans la `$MFT`, à ne pas confondre avec sa date d'ajout au `Shimcache`

{{< admonition type=tip title="A propos de la MFT" open=false >}}
La **MFT** est une **base de données** qui contient la liste de fichiers et répertoires du système.
Son champ **$SI** contient des informations sur l'horodatage du fichier (création, modification, dernier accès).
Ces **informations sont écrites par le noyau** et non par l'utilisateur (donc plus difficilement altérable).
{{< /admonition >}}

- Sa **position dans le cache** (les enregistrements les plus récents sont en premiers dans la liste)
- Sous *Windows XP* et *Windows 2003*, on récupère la **taille du fichier** et la **date de mise à jour du cache**
- Entre *Windows XP* et *Windows 8.1*, on récupère le **Flag Exec** qui indique s'il a déjà été lancé ou non [[4]](#references)

On note que renommer ou déplacer un fichier va le **remettre dans le Shimcache**.

Une trace très intéressante d'une intrusion peut être laissée lorsqu'un fichier est créé, puis que l'attaquant fait du **timestomping** sur celui-ci.

{{< admonition type=warning title="Timestomping" open=true >}}
Le **timestomping** est une technique utilisée par les attaquants qui consiste à manipuler l'horodatage d'un fichier pour le dissimuler avec d'autres fichiers plus anciens sur le système.
L'effet recherché est de donner une légitimité à l'existence d'un exécutable par exemple.
{{< /admonition >}}

On peut comparer les dates de dernière modification du `Shimcache` avec celles du système de fichiers, et une différence pourrait révéler cette technique d'évasion.
En effet, le `Shimcache` fait foi puisqu'il se réfère au **$SI de la MFT**.

## Les limites de cet artefact

Les entrées ne sont écrites dans le `Shimcache` que **lors du redémarrage de la machine**, ce qui peut rendre son analyse plus complexe dans le cadre d'une investigation forensique.
Cependant, un module Volatility permet de visualiser le Shimcache en RAM.

Les fichiers ajoutés dans le `Shimcache` sont uniquement ceux qui ont été vus dans `explorer.exe`, et pas au travers d'un `dir` dans un terminal par exemple.

Le **flag d'exécution** peut être ajouté dans le `Shimcache` s'il est disponible, mais **il ne fait pas foi** sur les distributions récentes de Windows (après W8.1) [[4][5]](#references).
Il est plus intéressant de corréler avec d'autres artefacts pour vérifier son exécution.

## It's dump time!

### AppCompatCacheParser

Pour dumper son `Shimcache`, on peut soit partir d'un dump des clés de registre (avec **FTK Imager** par exemple), soit dumper le cache en live.
Comme d'habitude sous Windows, on va utiliser un outil de la **suite Zimmerman**. 

```powershell
.\AppCompatCacheParser.exe  --csv C:\Users\user\Desktop\
```

On peut ensuite parser le fichier avec **Timeline Explorer** :

{{< image src="images/timeline_explorer_shimcache_dump.png" alt="Analyse du dump avec Timeline Explorer" caption="Analyse du dump avec Timeline Explorer" >}}

On retrouve bien les artefacts mentionnés dans la section **"L'intérêt forensic"**.

### Chainsaw

On peut également parser le `Shimcache` avec [Chainsaw de Withsecure](https://github.com/WithSecureLabs/chainsaw) [[6]](#references).
```powershell
.\chainsaw.exe analyse shimcache C:\Users\user\Desktop\system_hive --output shimcache.dmp
```

### Volatility

Un module volatility2 existe également pour consulter le `Shimcache` directement en mémoire [[7][8]](#references).
Si vous avez bien suivi, ce plugin répond exactement à une limitation évoquée plus haut, dans laquelle on voyait que le `Shimcache` était en RAM jusqu'au moment du redémarrage où il était enfin écrit.

```powershell
# On voit que sous Windows XP on a accès à la taille du fichier
python vol.py -f D:\Projects\Volatility\WinXPSP2x86.bin --profile=WinXPSP2x86 --kdbg=0x8054cde0 --dtb=0x39000 shimcachemem
Volatility Foundation Volatility Framework 2.5

Order Last Modified         Last Update           Exec  File Size  File Path
----- --------------------- --------------------- ----- ---------- ---------
    1 2012-11-27 01:42:21   2012-11-27 01:57:28              95104 \??\C:\mdd.exe
    2 2008-04-14 11:42:06   2012-11-27 01:56:17            8461312 \??\C:\WINDOWS\system32\SHELL32.dll
    3 2008-04-14 11:42:40   2012-11-27 01:56:17              28672 \??\C:\WINDOWS\system32\verclsid.exe

# On compare à des résultats W7 tirés du blog d'Andrea Fortuna
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

Le `Shimcache` est un artefact forensic riche en informations.
Lors d'une investigation, on l'analyse pour **faire de la corrélation** sur des exécutables qui sont (ou ont été) présents sur le système.
Cet artefact rend l'**effacement des traces** d'un attaquant plus complexe.
En revanche, il est plus difficile à analyser dans le cas où il n'est pas possible de redémarrer la machine.

## References

- [1] [Demystifying Shims](https://techcommunity.microsoft.com/t5/ask-the-performance-team/demystifying-shims-or-using-the-app-compat-toolkit-to-make-your/ba-p/374947)

- [2] [The Value of Shimcache for Investigators](https://www.mandiant.com/resources/blog/caching-out-the-val)

- [3] [Let's Talk About Shimcache - 13Cubed](https://www.youtube.com/watch?v=7byz1dR_CLg)

- [4] [Shimcache for Forensic](https://artefacts.help/windows_shimcache.html)

- [5] [The (Mis)Use of Artifact Categories](https://windowsir.blogspot.com/2022/02/the-misuse-of-artifact-categories.html)

- [6] [Chainsaw for Shimcache](https://labs.withsecure.com/tools/chainsaw-analyse-shimcache)

- [7] [Andrea Fortuna Blog](https://andreafortuna.org/2017/07/31/volatility-my-own-cheatsheet-part-6-windows-registry/)

- [8] [Volatility Shimcache Module](https://github.com/mandiant/Volatility-Plugins/blob/master/shimcachemem/README.md)