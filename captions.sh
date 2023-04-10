#!/usr/bin/env bash
VIDEO_ID=uu3NzgnAiMk
# wget https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId=$VIDEO_ID&key=$GOOGLE_API_KEY

URL="https://www.googleapis.com/youtube/v3/videos?id=7lCDEYXw3mM&key=$GOOGLE_API_KEY&part=snippet,contentDetails,statistics,status"

echo $URL
echo
wget $URL

