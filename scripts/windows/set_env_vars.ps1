############ ENVIRONMENT VARIABLES FOR LOCAL ############

[System.Environment]::SetEnvironmentVariable("LOCAL_MQTT_CLIENT_ID", "", "machine")
[System.Environment]::SetEnvironmentVariable("LOCAL_MQTT_PUB_TOPIC", "", "machine")
[System.Environment]::SetEnvironmentVariable("LOCAL_MQTT_SUB_TOPIC", "", "machine")
[System.Environment]::SetEnvironmentVariable("LOCAL_MQTT_HOSTNAME", "", "machine")
[System.Environment]::SetEnvironmentVariable("LOCAL_MQTT_USERNAME", "", "machine")
[System.Environment]::SetEnvironmentVariable("LOCAL_MQTT_PASSWORD", "", "machine")
[System.Environment]::SetEnvironmentVariable("LOCAL_MQTT_PORT", "", "machine")

############ ENVIRONMENT VARIABLES FOR CLOUD ############

[System.Environment]::SetEnvironmentVariable("AWS_SAGEMAKER_ACCESS_KEY_ID", "", "machine")
[System.Environment]::SetEnvironmentVariable("AWS_SAGEMAKER_SECRET_ACCESS_KEY", "", "machine")
[System.Environment]::SetEnvironmentVariable("AWS_SAGEMAKER_REGION", "", "machine")
[System.Environment]::SetEnvironmentVariable("AWS_SAGEMAKER_ENDPOINT", "", "machine")

[System.Environment]::SetEnvironmentVariable("AWS_KINESIS_VIDEO_STREAM_NAME", "", "machine")
[System.Environment]::SetEnvironmentVariable("AWS_KINESIS_VIDEO_STREAM_ACCESS_KEY_ID", "", "machine")
[System.Environment]::SetEnvironmentVariable("AWS_KINESIS_VIDEO_STREAM_SECRET_ACCESS_KEY", "", "machine")
[System.Environment]::SetEnvironmentVariable("AWS_KINESIS_VIDEO_STREAM_REGION", "", "machine")

[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_CLIENT_ID", "", "machine")
[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_PUB_TOPIC", "", "machine")
[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_SUB_TOPIC", "", "machine")
[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_HOSTNAME", "", "machine")
[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_CA_CERTS", "", "machine")
[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_CERTFILE", "", "machine")
[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_KEYFILE", "", "machine")
[System.Environment]::SetEnvironmentVariable("CLOUD_MQTT_PORT", "", "machine")

[System.Environment]::SetEnvironmentVariable("RDS_DB_HOSTNAME", "", "machine")
[System.Environment]::SetEnvironmentVariable("RDS_DB_USERNAME", "", "machine")
[System.Environment]::SetEnvironmentVariable("RDS_DB_PASSWORD", "", "machine")