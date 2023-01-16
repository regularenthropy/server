#! /usr/bin/env bash
rm new.txt
touch new.txt

function add () {
	curl ${*} | sed '/^#/d' | sed '/^!/d' > tmp.list
	cat tmp.list | sed 's/0.0.0.0/\  -/g' >> new.txt
}

add https://raw.githubusercontent.com/rimu/no-qanon/master/etc_hosts.txt
add https://raw.githubusercontent.com/antifa-n/pihole/master/blocklist.txt
add https://raw.githubusercontent.com/antifa-n/pihole/master/blocklist-alttech.txt
add https://raw.githubusercontent.com/antifa-n/pihole/master/blocklist-pop.txt
add https://raw.githubusercontent.com/marktron/fakenews/master/fakenews
add https://malware-filter.gitlab.io/malware-filter/urlhaus-filter-hosts.txt
add https://adguardteam.github.io/HostlistsRegistry/assets/filter_9.txt
add https://raw.githubusercontent.com/durablenapkin/scamblocklist/master/hosts.txt

sort new.txt | uniq > add_to_yml.txt

cat base.yml > new.yml
cat add_to_yml.txt >> new.yml

rm new.txt tmp.list add_to_yml.txt
