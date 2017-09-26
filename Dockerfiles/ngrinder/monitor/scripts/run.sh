#!/usr/bin/env bash
controller=$1
shift
if [ ! -n "$controller" ]
then
    echo "controller:port should be provided as an argument to download an agent"
    controller="controller:80"
    echo "use controller:80 as a default"    
fi
MONITOR_DOWNLOAD_URL="http://$controller/monitor/download"

monitor/download/ngrinder-monitor-3.4.tar
cd $BASE_DIR
echo "deleting pid..."
rm -rf $NGRINDER_MONIOTR_HOME/pid
if [ -e "$NGRINDER_MONITOR_BASE/run_monitor.sh" ]; then
    echo "monitor binary already exists."
else
    for i in {1..30};
    do
        wget -O ngrinder-monitor.tar -T 60 $MONITOR_DOWNLOAD_URL && break || sleep 10;
    done
    if [ ! -f "$BASE_DIR/ngrinder-monitor.tar" ];
    then
       echo "fail to download an monitor file from " $MONITOR_DOWNLOAD_URL
       exit 1
    fi
    tar -xvf ngrinder-monitor.tar
fi

$NGRINDER_MONITOR_BASE/run_monitor.sh $*