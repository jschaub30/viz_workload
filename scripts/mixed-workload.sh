#!/bin/bash
# Create a mixed workload script
# Copy script to each host (HOSTS variable, comma-separated)
# Run script on each host

SCRIPT_LOC="/tmp/mixed.viz_workload.sh"
TMP_FN="$HOME/.tmp.viz"
cat <<EOF > "$SCRIPT_LOC"
#!/bin/bash
# Simulate a workload with:
# - disk write
# - high cpu
# - disk read

cleanup () {
  rm -f "$TMP_FN"
  exit "$1"
}

trap 'cleanup 1' SIGTERM SIGINT # Cleanup tmp file if killed early

echo "Writing to disk"
dd if=/dev/random of="$TMP_FN" bs=1024k count=8192
sync
sleep 2

echo "Loading CPU on 4 threads"
timeout 30 taskset -c 0 bash -c "while true; do true; done;" &
timeout 30 taskset -c 1 bash -c "while true; do true; done;" &
timeout 30 taskset -c 2 bash -c "while true; do true; done;" &
timeout 30 taskset -c 3 bash -c "while true; do true; done;" &
wait
sleep 2

echo "Clearing disk cache prior to disk read"
echo 1 | sudo tee /proc/sys/vm/drop_caches

echo "Reading from disk"
dd if="$TMP_FN" of=/dev/null
sync
EOF

chmod +x "$SCRIPT_LOC"
HOSTS=$1
[ -z "$HOSTS" ] && HOSTS=$(hostname -s)
IFS=',' read -r -a hostname_array <<< "$HOSTS"

# Copy the file to each host
for HOST in "${hostname_array[@]}"; do
    echo "Copying workload script to $HOST"
    scp "$SCRIPT_LOC" "$HOST:$SCRIPT_LOC" &
done
wait

# Run the script on each host
# shellcheck disable=SC2029
for HOST in "${hostname_array[@]}"; do
    echo "Running $SCRIPT_LOC on $HOST"
    ssh "$HOST" "$SCRIPT_LOC" &
done

wait
