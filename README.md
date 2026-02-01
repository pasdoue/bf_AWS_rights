## General

This project has been released because, impossible to find robust library for brute forcing AWS IAM rights.

Tested those two projects but does not output same results... :  
https://github.com/andresriancho/enumerate-iam  
https://github.com/carlospolop/bf-aws-permissions  

## Information

**This code can take a while (up to 6min for total BF).**

This code is using official boto library and load dynamically all subfunctions of every services of boto (ie : iam,ec2...)

1. Set your creds & config inside files : https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html

> The script can support multiple profiles. So feel free to create plenty of them if needed ! :D
> Simple & minimalist example below : 

~/.aws/credentials : 
```bash
[default]
 aws_access_key_id = ASIA...NSQ
 aws_secret_access_key = WihcB......PiMeFULn
 aws_session_token = IQoJb3JpZ2luX2VjEDcaCXVzLWVhc3QtMiJ.....Hm25smvGxg=
```

~/.aws/config : 
```bash
[default]
 region = us-east-2
```

2. Generate AWS boto config file first launch or force it

If you run this script the first time with or without params, it will perform an update of sessions and functions available by boto first.
```bash
python3 main.py -u
```

3. Start gathering info

> Help

```bash
[*]
          ____  ______        __          _______       _____  _____ _____ _    _ _______ _____
         |  _ \|  ____|      /\ \        / / ____|     |  __ \|_   _/ ____| |  | |__   __/ ____|
         | |_) | |__ ______ /  \ \  /\  / / (___ ______| |__) | | || |  __| |__| |  | | | (___
         |  _ <|  __|______/ /\ \ \/  \/ / \___ \______|  _  /  | || | |_ |  __  |  | |  \___ \ 
         | |_) | |        / ____ \  /\  /  ____) |     | | \ \ _| || |__| | |  | |  | |  ____) |
         |____/|_|       /_/    \_\/  \/  |_____/      |_|  \_\_____\_____|_|  |_|  |_| |_____/
         Made by pasdoue

usage: main.py [-h] [--credentials-file CREDENTIALS_FILE] [--config-file CONFIG_FILE] [-t THREADS] [--thread-timeout THREAD_TIMEOUT] [-u] [-b [PARAMETER ...]] [-w [PARAMETER ...]] [-p]
               [--unsafe-mode]

Bruteforce AWS rights with boto3

options:
  -h, --help            show this help message and exit
  --credentials-file CREDENTIALS_FILE
                        AWS credentials file
  --config-file CONFIG_FILE
                        AWS config file
  -t THREADS, --threads THREADS
                        Number of threads to use
  --thread-timeout THREAD_TIMEOUT
                        Timeout consumed before killing thread
  -u, --update-services
                        Update dynamically list of AWS services and associated functions
  -b [PARAMETER ...], --black-list [PARAMETER ...]
                        List of services to remove separated by comma. Launch script with -p to see services
  -w [PARAMETER ...], --white-list [PARAMETER ...]
                        List of services to whitelist/scan separated by comma. Launch script with -p to see services
  -p, --print-services  List of all available services
  --unsafe-mode         Perform potentially destructive functions. Disabled by default.
```

Launch scan on all services : 
```bash
python3 main.py
```

Show list of available services : 
```bash
python3 main.py -p
```

Scan using white-list : 
```bash
python3 main.py -w ec2 sts pricing dynamodb
```

Show number of calls that will be performed using only some services : 
```bash
python3 main.py -p -w ec2 sts dynamodb
```

Scan using black-list : 
```bash
python3 main.py -b cloudhsm cloudhsmv2 sms dynamodb
```

Scan using black-list & white-list (will perform scan on white list without "dynamodb" service): 
```bash
python3 main.py -w ec2 sts pricing dynamodb -b cloudhsm cloudhsmv2 sms dynamodb
```

Total BF (unsafe mode, not recommended if you don't know what you do)
```bash
python3 main.py --unsafe-mode
```

## TBD : 

- [ ] Implement V3 (but shush it's a secret :D)
- [ ] Detect if some results will be erased and trigger a warning if different from previous run
- [ ] Maybe chunk output json files that are too big (but make it optional)

## Bonus

All functions prefix i could find (255). This is helping to determine which function can be called without "damages"

```text
abort_
accept_
acknowledge_
activate_
add_
admin_
advertise_
allocate_
allow_
analyze_
apply_
approve_
archive_
assign_
associate_
assume_
attach_
authorize_
back_
backtrack_
batch_
begin_
build_
bulk_
bundle_
calculate_
can_
cancel_
change_
channel_
chat_
check_
checkout_
claim_
classify_
clear_
clone_
close_
commit_
compare_
complete_
compose_
configure_
confirm_
connect_
contains_
continue_
converse_
convert_
copy_
count_
create_
deactivate_
deauthorize_
decline_
decode_
decrease_
decrypt_
define_
deliver_
deny_
deploy_
deprecate_
deprovision_
deregister_
derive_
describe_
detach_
detect_
disable_
disassociate_
discard_
disconnect_
discover_
dismiss_
dispose_
dissociate_
distribute_
domain_
download_
enable_
encrypt_
enter_
estimate_
evaluate_
exchange_
execute_
exit_
expire_
export_
extend_
failover_
filter_
finalize_
flush_
forecast_
forget_
forgot_
generate_
get_
global_
grant_
group_
head_
import_
increase_
index_
infer_
ingest_
initialize_
initiate_
install_
instantiate_
invalidate_
invite_
invoke_
is_
issue_
join_
label_
list_
lock_
logout_
lookup_
manage_
mark_
merge_
meter_
migrate_
modify_
monitor_
move_
notify_
open_
opt_
optimize_
override_
pause_
peer_
phone_
poll_
populate_
post_
predict_
prepare_
preview_
promote_
provide_
provision_
publish_
purchase_
purge_
push_
put_
query_
re_
read_
rebalance_
reboot_
rebuild_
receive_
recognize_
record_
redact_
redrive_
refresh_
regenerate_
register_
reimport_
reject_
release_
reload_
remove_
rename_
render_
renew_
reorder_
replace_
replicate_
report_
request_
resend_
reserve_
reset_
resize_
resolve_
respond_
restart_
restore_
resume_
resync_
retire_
retrieve_
retry_
return_
reverse_
revoke_
rollback_
rotate_
run_
sample_
scan_
schedule_
search_
select_
send_
set_
setup_
share_
shutdown_
sign_
signal_
simulate_
skip_
snap_
split_
start_
stop_
stream_
submit_
subscribe_
suspend_
swap_
switchover_
sync_
synthesize_
tag_
terminate_
test_
transact_
transfer_
translate_
unarchive_
unassign_
undeploy_
undeprecate_
ungroup_
unlabel_
unlink_
unlock_
unmonitor_
unpeer_
unregister_
unshare_
unsubscribe_
untag_
update_
upgrade_
upload_
validate_
verify_
view_
vote_
withdraw_
write_
```
