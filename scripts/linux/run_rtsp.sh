#This command works on RPI
libcamera-vid -o - -t 0 --width 1280 --height 1080 -n | cvlc -vvv stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8554/}' :demux=h264
