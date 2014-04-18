#!/bin/sh

echo "Initiating..."

while :
do
    date --rfc-3339=seconds | sed -r -e "s/(.*)/\1 STARTED/"
    DISPLAY="host:0.0" python skype2irc.py
    rc=$?
    date --rfc-3339=seconds | sed -r -e "s/(.*)/\1 STOPPED/"
    # interpret bot exit code
    if [ $rc -eq 0 ] ; then
        echo 'Terminating gracefully.'
        exit 0
    elif [ $rc -eq 10 ] ; then
        echo 'Restarting immediately upon request.'
    else
        sleep 15
    fi
done
