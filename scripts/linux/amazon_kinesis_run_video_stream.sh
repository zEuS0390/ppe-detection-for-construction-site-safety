gst-launch-1.0 libcamerasrc ! video/x-raw,width=640,height=480,framerate=30/1,format=I420 ! videoconvert ! v4l2h264enc extra-controls=controls,repeat_sequence_header=1 ! video/x-h264,level='(string)4' ! h264parse ! video/x-h264,stream-format=avc, alignment=au,width=640,height=480,framerate=30/1 ! kvssink stream-name=ppedetection-videostream access-key=AKIAUMSL53LIIT4DU5FZ secret-key=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 aws-region=ap-southeast-1
