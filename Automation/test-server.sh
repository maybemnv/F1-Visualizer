#!/bin/bash

if ! lsof -i :8000
then
    UTC=$(date)
    bash ~/F1-Visualizer/Automation/start-server.sh
    aws sns publish --topic-arn arn:aws:sns:us-east-2:637423600104:F1-Visualizer --message file://~/F1-Visualizer/Automation/dash.log --subject "Server Health Warning - $UTC"
fi
