#!/bin/bash

[ $# -ne 2 ] && echo USAGE: $0 TARGET_FN DELAY_SEC && exit 1
TARGET_FN=$1
DELAY_SEC=$2

TM=`date +%g%m%d%H%M%S`
echo -n "timestamp" > $TARGET_FN
IBCARDS=/sys/class/infiniband/mlx*

for CARD in $IBCARDS
do
  C=`echo $CARD | awk -F "/" '{print $NF}'`
  PORTS=$CARD/ports/*

  for PORT in $PORTS
  do
    P=`echo $PORT | awk -F "/" '{print $NF}'`
    declare ${C}_${P}=$PORT

    echo -n ", ${C}_${P}_xmit" >> $TARGET_FN
    echo -n ", ${C}_${P}_recv" >> $TARGET_FN

    IBLIST="$IBLIST ${C}_${P}"
  done
done

echo "" >> $TARGET_FN


for IB in $IBLIST
do
  declare ${IB}_XMIT_OLD=`cat ${!IB}/counters/port_xmit_data`
  declare ${IB}_RECV_OLD=`cat ${!IB}/counters/port_rcv_data`
done

STOP_FN=/tmp/${USER}/viz_workload/stop-ib
rm -f $STOP_FN

while [ ! -f $STOP_FN ]
do
  TM=`date +"%s"`
  echo -n  $TM >> $TARGET_FN

  for IB in $IBLIST
  do
    XMIT=`cat ${!IB}/counters/port_xmit_data`
    RECV=`cat ${!IB}/counters/port_rcv_data`


    XMIT_OLD="${IB}_XMIT_OLD"
    RECV_OLD="${IB}_RECV_OLD"

    X=`expr $XMIT - ${!XMIT_OLD}`
    R=`expr $RECV - ${!RECV_OLD}`

    echo  -n ", $X, $R" >> $TARGET_FN

    declare ${IB}_XMIT_OLD=$XMIT
    declare ${IB}_RECV_OLD=$RECV

  done 
  echo "" >> $TARGET_FN
  sleep $DELAY_SEC
done
rm $STOP_FN
