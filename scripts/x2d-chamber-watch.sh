#!/bin/bash
# Poll the X2D every 5 min (read-only MQTT via scripts/x2d-status.py) and print
# one line per event: print start, chamber >= ALERT_C (repeat every 15 min),
# progress every 30 min, and the terminal state (FINISH / FAILED / PAUSE).
# Waits up to 2 h for a job to start; ignores a stale FAILED/FINISH state from
# a previous job. Every poll is appended to $LOG as CSV.
# Usage: scripts/x2d-chamber-watch.sh [ALERT_C] [LOG]   (defaults 40, /tmp/x2d-chamber-log.csv)
cd "$(dirname "$0")/.." || exit 1
ALERT_C=${1:-40}
LOG=${2:-/tmp/x2d-chamber-log.csv}
echo "time,state,progress,layer,bed,nozzle,chamber" >> "$LOG"
seen_running=0; ticks=0; idle_ticks=0; last_alert=-9
while true; do
  out=$(timeout 90 .venv/bin/python scripts/x2d-status.py 2>&1) || true
  state=$(sed -n 's/^state: \([A-Z]*\).*/\1/p' <<<"$out")
  prog=$(sed -n 's/.*progress: \([0-9]*\)%.*/\1/p' <<<"$out")
  layer=$(sed -n 's/.*layer \([0-9]*\/[0-9]*\).*/\1/p' <<<"$out")
  bed=$(sed -n 's/^temps: bed \([0-9.]*\).*/\1/p' <<<"$out")
  noz=$(sed -n 's/.*nozzle \([0-9.]*\)\/.*/\1/p' <<<"$out")
  ch=$(sed -n 's/.*chamber \([0-9.None]*\).*/\1/p' <<<"$out")
  now=$(date +%H:%M)
  echo "$now,$state,$prog,$layer,$bed,$noz,$ch" >> "$LOG"
  if [ -z "$state" ]; then
    echo "$now no status from printer (connect failed or timeout)"
  elif [ "$state" = "RUNNING" ] || [ "$state" = "PREPARE" ]; then
    idle_ticks=0
    if [ $seen_running -eq 0 ]; then seen_running=1; echo "$now print running: $prog% layer $layer bed $bed nozzle $noz chamber $ch"; fi
    chi=${ch%.*}
    if [ -n "$chi" ] && [ "$chi" != "None" ] && [ "$chi" -ge "$ALERT_C" ] && [ $((ticks - last_alert)) -ge 3 ]; then
      last_alert=$ticks; echo "$now CHAMBER HIGH: $ch C (bed $bed nozzle $noz) at $prog% layer $layer"
    fi
    if [ $((ticks % 6)) -eq 0 ] && [ $ticks -gt 0 ]; then echo "$now progress: $prog% layer $layer chamber $ch C bed $bed nozzle $noz"; fi
  elif { [ "$state" = "FAILED" ] || [ "$state" = "PAUSE" ]; } && [ $seen_running -eq 1 ]; then
    echo "$now PRINT $state at $prog% layer $layer chamber $ch: $(grep -E 'hms|print_error' <<<"$out")"
    [ "$state" = "FAILED" ] && exit 0
  elif [ "$state" = "FINISH" ] || [ "$state" = "IDLE" ] || [ "$state" = "FAILED" ] || [ "$state" = "PAUSE" ]; then
    if [ $seen_running -eq 1 ]; then echo "$now print finished ($state) layer $layer, chamber $ch C"; exit 0; fi
    idle_ticks=$((idle_ticks + 1))
    if [ $idle_ticks -ge 24 ]; then echo "$now no print started in 2 h, stopping the watch"; exit 0; fi
  fi
  ticks=$((ticks + 1))
  sleep 300
done
