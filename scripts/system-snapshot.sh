#!/bin/bash
# Collect data from a series of linux commands, then create html by
# substituting each result into template.html using tags

[ $# -ne 1 ] && echo Usage: $0 FILENAME && exit 1

HTML_FN=$1
rm -f $HTML_FN

ALL_COMMANDS=("hostname" "ifconfig -a" "lscpu" "cat /proc/cpuinfo" "cat /proc/meminfo" "uname -a" \
    "lsblk" "lspci" "df -h" "cat /etc/issue" "hostname -I" \
    "date +%Y%m%d-%H%M%S" "lstopo")
ALL_TAGS=("TAG_HOSTNAME" "TAG_IFCONFIG" "TAG_LSCPU" "TAG_CPUINFO" "TAG_MEMINFO" "TAG_LINUX" \
    "TAG_LSBLK" "TAG_LSPCI" "TAG_DF" "TAG_OS" "TAG_IPADDR" \
    "TAG_DATETIME" "TAG_LSTOPO")

INDEX=$(cat summary-template.html)

TMP_FN=tmp$(date +%N) # Timestamp nanoseconds

for ((i = 0; i < ${#ALL_COMMANDS[@]}; i++))
do
    COMMAND=${ALL_COMMANDS[i]}
    TAG=${ALL_TAGS[i]}
    # echo command is \"$COMMAND\", search is \"${TAG}\"
    $COMMAND 1>$TMP_FN 2>/dev/null 
    if [ $? -eq 0 ]; then
        DATA=$(cat $TMP_FN | perl -pe "s/\n/\<br\/\>/g")  # newlines --> line breaks
        DATA=$(echo $DATA | perl -pe "s/<br\/>$//")   # Remove trailing line break
        HTML1=$(echo $INDEX | perl -pe "s/${TAG}.*//")  # before tag
        HTML2=$(echo $INDEX | perl -pe "s/^.*${TAG}//") # after tag
        INDEX=$(echo $HTML1 $DATA $HTML2) # combine before and after
        echo $INDEX > $HTML_FN
    fi
    rm -f $TMP_FN
done
