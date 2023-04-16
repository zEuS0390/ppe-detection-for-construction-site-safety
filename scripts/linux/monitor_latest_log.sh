# Get command line argument to get the base directory
current_dir=$1

# Get the most recent file created
latest_log=$(eval ls -Art $current_dir | tail -n 1)

# Open and continuously monitor the log file
tail -f $current_dir/$latest_log
