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

