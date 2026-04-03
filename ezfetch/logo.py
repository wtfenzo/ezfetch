"""ASCII logo art and distro detection."""

import platform
from pathlib import Path
from typing import List, Optional

LOGOS = {
    "arch": r"""                     
                  -`                     
                 .o+`                    
                `ooo/                    
               `+oooo:                   
              `+oooooo:                  
              -+oooooo+:                 
            `/:-:++oooo+:                
           `/++++/+++++++:               
          `/++++++++++++++:              
         `/+++ooooooooooooo/`            
        ./ooosssso++osssssso+`           
       .oossssso-````/ossssss+`          
      -osssssso.      :ssssssso.         
     :osssssss/        osssso+++.        
    /ossssssss/        +ssssooo/-        
  `/ossssso+/:-        -:/+osssso+-      
 `+sso+:-`                 `.-/+oso:     
`++:.                           `-/+/    
.`                                 `/    """,

    "debian": r"""
       _,met$$$$$gg.
    ,g$$$$$$$$$$$$$$$P.
  ,g$$P\"     \"\"\"Y$$.".
 ,$$P'              `$$$.
',$$P       ,ggs.     `$$b:
`d$$'     ,$P\"'   .    $$$
 $$P      d$'     ,    $$P
 $$:      $$.   -    ,d$$'
 $$;      Y$b._   _,d$P'
 Y$$.    `.`\"Y$$$$P\"'
 `$$b      \"-.__
  `Y$$
   `Y$$.
     `$$b.
       `Y$$b.
          `\"Y$b._
              `\"\"\"\" """,

    "ubuntu": r"""
            .-/+oossssoo+/-.
        `:+ssssssssssssssssss+:`
      -+ssssssssssssssssssyyssss+-
    .ossssssssssssssssss/    /ssssso.
   /sssssssssssssssss/      /ssssssss/
  +sssssssssssssss/        /ssssssssss+
 /ssssssssssssss/         /sssssssssssss
.ssssssssssssss+         +sssssssssssssss.
+ssssssssssssss/        /ssssssssssssssss+
ssssssssssssssss+/:  -/sssssssssssssssssss
ssssssssssssssssssssssssssssssssssssssssss
+ssssssssssssssssssssssssssssssssssssssss+
.ssssssssssssssssssssssssssssssssssssssss.
 /ssssssssssssssssssssssssssssssssssssss/
  +sssssssssssssssssssssssssssssssssss+
   /sssssssssssssssssssssssssssssssss/
    .ossssssssssssssssssssssssssssso.
      -+sssssssssssssssssssssssss+-
        `:+ssssssssssssssssss+:`
            .-/+oossssoo+/-.""",

    "mint": r"""
 MMMMMMMMMMMMMMMMMMMMMMMMMmds+.
 MMm----::-://////////////oymNMd+`
 MMd      /++                -sNMd:
 MMNso/`  dMM    `.::-. .-::.`/NMd
 ddddMMh  dMM   :hNMNMNhNMNMNh: `NMm
     NMm  dMM  .NMN/-+MMM+-/NMN` dMM
     NMm  dMM  -MMm  `MMM   dMM. dMM
     NMm  dMM  -MMm  `MMM   dMM. dMM
     NMm  dMM  .mmd  `mmm   yMM. dMM
     NMm  dMM`  ..`   ...   ydm. dMM
     hMM- +MMd/-------...-:sdds  dMM
     -NMm- :hNMNNNmdddddddddy/`  dMM
      -dMNs-``-::::-------.``    dMM
       `/dMNmy+/:-------------:/yMMM
          ./ydNMMMMMMMMMMMMMMMMMMMMM
             .MMMMMMMMMMMMMMMMMMM""",

    "mac": r"""
                    'c.
                 ,xNMM.
               .OMMMMo
               OMMM0,
     .;loddo:' loolloddol;.
   cKMMMMMMMMMMNWMMMMMMMMMM0:
 .KMMMMMMMMMMMMMMMMMMMMMMMWd.
 XMMMMMMMMMMMMMMMMMMMMMMMX.
;MMMMMMMMMMMMMMMMMMMMMMMM:
:MMMMMMMMMMMMMMMMMMMMMMMM:
.MMMMMMMMMMMMMMMMMMMMMMMMX.
 kMMMMMMMMMMMMMMMMMMMMMMMMWd.
 .XMMMMMMMMMMMMMMMMMMMMMMMMMMk
  .XMMMMMMMMMMMMMMMMMMMMMMMMK.
    kMMMMMMMMMMMMMMMMMMMMMMd
     ;KMMMMMMMWXXWMMMMMMMk.
       .cooc,.    .,coo:.""",

    "windows": r"""                                   
                                ..,
                    ....,,:;+ccllll
      ...,,+:;  cllllllllllllllllll
,cclllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
                                    
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
llllllllllllll  lllllllllllllllllll
`'ccllllllllll  lllllllllllllllllll
       `' \*::  :ccllllllllllllllll
                       ````''*::cll""",
    
    "fedora": r"""
          /:-------------:\          
       :-------------------::       
     :-----------/shhOHbmp---:\     
   /-----------omMMMNNNMMD  ---:   
  :-----------sMMMMNMNMP.    ---:  
 :-----------:MMMdP-------    ---\
,------------:MMMd--------    ---:
:------------:MMMd-------    .---:
:----    oNMMMMMMMMMNho     .----:
:--     .+shhhMMMmhhy++   .------/
:-    -------:MMMd--------------:
:-   --------/MMMd-------------;
:-    ------/hMMMy------------:
:-- :dMNdhhdNMMNo------------;
:---:sdNMMMMNds:------------:
:------:://:-------------::
:---------------------://""",

    "redhat": r"""                                   .
           .MMM..:MMMMMMM                   
          MMMMMMMMMMMMMMMM                  
          MMMMMMMMMMMMMMMMMM.              
         MMMMMMMMMMMMMMMMMMMM              
        ,MMMMMMMMMMMMMMMMMMMM:             
        MMMMMMMMMMMMMMMMMMMMMM             
  .MMMM'  MMMMMMMMMMMMMMMMMMMM            
 MMMMMM    `MMMMMMMMMMMMMMMMMM.             
MMMMMMMM      MMMMMMMMMMMMMMMM .          
MMMMMMMMM.       `MMMMMMMMMMM' MM.        
MMMMMMMMMMM.                     MM        
`MMMMMMMMMMMMM.                 MM'           
 `MMMMMMMMMMMMMMMMM.           MM'         
    MMMMMMMMMMMMMMMMMMMMMMMMMM'           
      MMMMMMMMMMMMMMMMMMMMM'              
         MMMMMMMMMMMMMMMM'                     
            `MMMMMMMM'                 
                                        """,
    
    "manjaro": r"""
██████████████████  ████████
██████████████████  ████████
██████████████████  ████████
██████████████████  ████████
████████            ████████
████████  ████████  ████████
████████  ████████  ████████
████████  ████████  ████████
████████  ████████  ████████
████████  ████████  ████████
████████  ████████  ████████
████████  ████████  ████████
████████  ████████  ████████
████████  ████████  ████████""",
    
    "popos": r"""
             /////////////
         /////////////////////
      ///////*767////////////////
    //////7676767676*//////////////
   /////76767//7676767//////////////
  /////767676///*76767///////////////
 ///////767676///76767.///7676*///////
/////////767676//76767///767676////////
//////////76767676767////76767/////////
///////////76767676//////7676//////////
////////////,7676,///////767///////////
/////////////*7676///////76////////////
///////////////7676////////////////////
 ///////////////7676///767////////////
  //////////////////////'////////////
   //////.7676767676767676767,//////
    /////767676767676767676767/////
      ///////////////////////////
         /////////////////////
             /////////////""",
    
    "alpine": r"""
       .hddddddddddddddddddddddh.
      :dddddddddddddddddddddddddd:
     /dddddddddddddddddddddddddddd/
    +dddddddddddddddddddddddddddddd+
  `sdddddddddddddddddddddddddddddddds`
 `ydddddddddddd++hdddddddddddddddddddy`
.hddddddddddd+`  `+ddddh:-sdddddddddddh.
hdddddddddd+`      `+y:    .sddddddddddh
ddddddddh+`   `//`   `.`     -sddddddddd
ddddddh+`   `/hddh/`   `:s-    -sddddddd
ddddh+`   `/+/dddddh/`   `+s-    -sddddd
ddd+`   `/o` :dddddddh/`   `oy-    .yddd
hdddyo+ohddyosdddddddddho+oydddy++ohdddh
.hddddddddddddddddddddddddddddddddddddh.
 `yddddddddddddddddddddddddddddddddddy`
  `sdddddddddddddddddddddddddddddddds`
    +dddddddddddddddddddddddddddddd+
     /dddddddddddddddddddddddddddd/
      :dddddddddddddddddddddddddd:
       .hddddddddddddddddddddddh.""",
    
    "gentoo": r"""
         -/oyddmdhs+:.
     -odNMMMMMMMMNNmhy+-`
   -yNMMMMMMMMMMMNNNmmdhy+-
 `omMMMMMMMMMMMMNmdmmmmddhhy/`
 omMMMMMMMMMMMNhhyyyohmdddhhhdo`
.ydMMMMMMMMMMdhs++so/smdddhhhhdm+`
 oyhdmNMMMMMMMNdyooydmddddhhhhyhNd.
  :oyhhdNNMMMMMMMNNNmmdddhhhhhyymMh
    .:+sydNMMMMMNNNmmmdddhhhhhhmMmy
       /mMMMMMMNNNmmmdddhhhhhmMNhs:
    `oNMMMMMMMNNNmmmddddhhdmMNhs+`
  `sNMMMMMMMMNNNmmmdddddmNMmhs/.
 /NMMMMMMMMNNNNmmmdddmNMNdso:`
+MMMMMMMNNNNNmmmmdmNMNdso/-
yMMNNNNNNNmmmmmNNMmhs+/-`
/hMMNNNNNNNNMNdhs++/-`
`/ohdmmddhys+++/:.`
  `-//////:--.""",
    
    "kali": r"""
      ,.....                                       
  ----`   `..,;:ccc,.                             
           ......''';lxO.                          
.....''''..........,:ld;                          
           .';;;:::;,,.x,                          
      ..'''.            0Xxoc:,.  ...              
  ....                ,ONkc;,;cokOdc',.            
 .                   OMo           ':do.           
                    dMc               :OO;         
                    0M.                 .:o.       
                    ;Wd                            
                     ;XO,                          
                       ,d0Odlc;,..                 
                           ..',;:cdOOd::,.         
                                    .:d;.':;.      
                                       'd,  .'     
                                         ;l   ..   
                                          .o       
                                            c      
                                            .'     
                                             .""",

    "linux": r"""
        .--.
       |o_o |
       |:_/ |
      //   \ \
     (|     | )
    /'\_   _/`\
    \___)=(___/""",
}

LOGOS["macos"] = LOGOS["darwin"] = LOGOS["mac"]
LOGOS["pop"] = LOGOS["popos"]
LOGOS["tux"] = LOGOS["linux"]
LOGOS["rhel"] = LOGOS["centos"] = LOGOS["rocky"] = LOGOS["alma"] = LOGOS["redhat"]

def detect_distro() -> str:
    """Detect the current OS/distro and return the matching logo key."""
    s = platform.system().lower()
    if s == "darwin":
        return "mac"
    if s == "windows":
        return "windows"
    if s == "linux":
        try:
            data = {}
            for line in Path("/etc/os-release").read_text(encoding="utf-8").splitlines():
                if "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip().lower()] = v.strip().strip('"').lower()
            lookup = {
                "arch": "arch", "ubuntu": "ubuntu", "debian": "debian",
                "linuxmint": "mint", "fedora": "fedora", "manjaro": "manjaro",
                "pop": "popos", "alpine": "alpine", "gentoo": "gentoo",
                "kali": "kali", "rhel": "redhat", "centos": "redhat",
                "rocky": "redhat", "alma": "redhat",
                "opensuse": "fedora", "suse": "fedora",
                "void": "linux", "nixos": "linux", "endeavouros": "arch",
                "artix": "arch", "garuda": "arch",
            }
            # Check ID first, then fall back to ID_LIKE for derivative distros
            for id_field in ("id", "id_like"):
                distro_id = data.get(id_field, "")
                for key, logo in lookup.items():
                    if key in distro_id:
                        return logo
        except Exception:
            pass
        return "linux"
    return "linux"

def get_logo(name: Optional[str] = None, custom_path: Optional[str] = None) -> str:
    """Return ASCII logo art for the given distro name, or auto-detect."""
    if isinstance(custom_path, (str, Path)) and custom_path:
        try:
            return Path(custom_path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError, TypeError, ValueError):
            pass
    if isinstance(name, str):
        key = name.strip().lower()
    elif name is None:
        key = detect_distro()
    else:
        key = str(name).strip().lower()
    return LOGOS.get(key or detect_distro(), LOGOS["linux"])


def list_logos() -> List[str]:
    """Return sorted list of available logo names."""
    return sorted(set(LOGOS.keys()))
