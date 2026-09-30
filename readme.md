Задание 1
=========

    >teem@teem:/etc$ grep -o "^[^:]*" passwd | sort
    _apt
    avahi
    avahi-autoipd
    backup
    bin
    colord
    cups-browsed
    cups-pk-helper
    daemon
    dhcpcd
    dnsmasq
    _flatpak
    fwupd-refresh
    games
    geoclue
    hplip
    irc
    kernoops
    lightdm
    list
    lp
    mail
    man
    messagebus
    news
    nm-openvpn
    polkitd
    proxy
    root
    rtkit
    saned
    speech-dispatcher
    sssd
    sync
    sys
    syslog
    systemd-coredump
    systemd-network
    systemd-resolve
    systemd-timesync
    tcpdump
    teem
    tss
    usbmux
    uucp
    uuidd
    www-data



Задание 2
=========

    >teem@teem:/etc$  grep -v '^#' protocols | awk 'NF {print $2, $1}'|sort -rn | head -5
    262 mptcp
    143 ethernet
    142 rohc
    141 wesp
    140 shim6
    
Задание 3
=========

    #!/bin/bash
    
    in=$1
    len=${#in}
    
    printf "+-"
    for ((i = 0; i < len; i++)); do
        printf "-"
    done
    printf -- "-+"
    printf -- "\n| $in |\n"
    printf "+-"
    for ((i = 0; i < len; i++)); do
        printf "-"
    done
    printf -- "-+"

Задание 4
=========

	>teem@DESKTOP-6FJQ3M1:~$ cat example_code.cpp | sed 's/[^a-z_ ]/ /g'| tr -s '[[:space:]]' '\n' | sort | uniq

	build_tree_objects
	cin
	cl_application
	cout
	endl
	exec_app
	find
	h
	hpp
	if
	include
	int
	iostream
	main
	namespace
	npos
	nullptr
	ob_application
	return
	root_name
	set
	std
	stdio
	stdlib
	string
	using

Задание 5
=========

    >teem@teem:~/School/ConUpr$ ./reg test
    Done

reg
-----

    #!/bin/bash

    in=$1
    len=${#in}

    printf "+-"
    for ((i = 0; i < len; i++)); do
        printf "-"
    done
    printf -- "-+"
    printf -- "\n| $in |\n"
    printf "+-"
    for ((i = 0; i < len; i++)); do
        printf "-"
    done
    printf -- "-+"

Задание 6
=========

    >teem@teem:~/School/ConUpr/timofei-oreshin-cm$ ./check_comment example_code.py
    True

check_comment
-------------

#!/bin/bash

    line=$(head -n 1 $1)
    if [[ "$1" == *".py"* ]]; then
        if [[ $line =~ ^# ]]; then
            echo True
        else
            echo False
        fi
    elif [[ "$1" == *".js"* || "$1" == *".c" ]]; then
        if [[ $line =~ ^// ]]; then
            echo True
        else
            echo False
        fi
    else
        echo "Unsupported file format"
    fi

Задание 7
=========

    >teem@teem:~/School/ConUpr/timofei-oreshin-cm/T7_finddups$ ./find_dups 
    d41d8cd98f00b204e9800998ecf8427e  ./ex
    d41d8cd98f00b204e9800998ecf8427e  ./exdir/ex1

find_dups
---------

    #!/bin/bash

    dir="${1:-.}"
    find $dir -type f -exec md5sum {} + | sort | uniq -w32 -D

Задание 8
=========

    >teem@teem:~/School/ConUpr/timofei-oreshin-cm$ ./archiver txt
    ./example_for_archiver/a.txt
    ./example_for_archiver/c.txt
    ./example_for_archiver/b.txt
    ./example_for_archiver/d.txt
    Done

archiver
--------

    #!/bin/bash

    dir="${1:-.}"
    find $dir -type f -exec md5sum {} + | sort | uniq -w32 -D

Задание 9
=========

    >teem@teem:~/School/ConUpr/timofei-oreshin-cm/T9_tabfix$ ./tabfix tabfix_in out
    Done

tabfix
------

    #!/bin/bash

    sed 's/    /\t/g' $1 >> $2
    echo Done

Задание 10
=========

    >teem@teem:~/School/ConUpr/timofei-oreshin-cm/T10_findempty$ ./find_empty /etc
    /etc/subgid-
    /etc/legal
    /etc/libpaper.d
    /etc/.pwd.lock
    find: ‘/etc/credstore.encrypted’: Permission denied
    /etc/opt
    /etc/colord
    /etc/keyutils
    /etc/usb_modeswitch.d
    /etc/guest-session
    /etc/plymouth
    /etc/subuid-
    find: ‘/etc/credstore’: Permission denied
    /etc/binfmt.d

find_empty
----------

    #!/bin/bash

    find $1 -maxdepth 1 -empty 

