## General

This project has been released because, impossible to find robust library for brute forcing AWS IAM rights.

Tested those two projects but does not output same results... : 
https://github.com/andresriancho/enumerate-iam
https://github.com/carlospolop/bf-aws-permissions


## Information

**This code can take a while (up to 6min for total BF).**

This code is using official boto library and load dynamically all subfunctions of every services of boto (ie : iam,ec2...)

You have multiple run configurations : 

1. Set your creds (config file way or environment) : 

> Config file

~/.aws/credentials : 
```bash
[default]
 aws_access_key_id = ASIA...NSQ
 aws_secret_access_key = WihcB......PiMeFULn
 aws_session_token = IQoJb3JpZ2luX2VjEDcaCXVzLWVhc3QtMiJHMEUCIDOTfJOvylz5TcxuVQaGyvwpBAMzX69MtSxa8q6aPfiOAiEAhWAQxWaBES8i6ErEmU+uNrGdyeNqbIyb+bbByjogpdMquAUIQRAAGgw1MzkyNDc0ODc5NjEiDIoIO3vypZCq8+yyGiqVBT45BFVrKuc2f71fxgEe9eLQ+L9UunN/FvfDqUTNDfvGeHR+M1SqCMpNoVrOqzZ49hZvO8cVTambJxogfGxzm703K/azlgWg65dtp0McxfzN8qQd2uhBLCjlqSwYHc6Zhxb5UEK0GCM3ATJI3zUqdZwAzIeeOUQNgsajnzkV/NvyEbbw0uCa0DTyKWJhvbsGnXf3vkxh/MNelC6FPGfv38L2MxiK/xvzzqsP20GkXLGGxgWrr3i910K96Tu0z/It7qbZNtMwxpDxsU2GvrFFWMDa7ZUSDFTdFU+SekG/J2hUtvg0oMvFUZ07phCPE7cyMa02MBH0Y9J9YvChpX5Jj9NppvwT95HMOI72dXaciVK+ctXkEswzW+ahNFCemeN75JhkX/Xn8co5frOnxXwFY5sX+2K+ia2Nxy9+nrjNbs+CA/CSalYL75R1haiEtLzaA3/P/uluPYvRhm2LqirG3V3iFzFfEzJeYWm0NhyoPnaQlATleXKVALi1qiHb5s7BpEXnK93ZeqL+TIGvwO0jUY7EWKBy3UuGXeYyohbVwTcJoLIp5P6DOv7SfWrxaFN9GH4MZGVY8MURt+hirqQnw3X/FpljY32D37lcYK+7uxs4VcpICAbFRphA4Agk4sOzqgFAnn4SmKhYyTd36FsQKSvTpOxfGDxU+F7cZNE3C00WOWAd7l2QTH7vHePQZLKX1Wh/YIW19QsLttV1hRkysPME/OfGIVKtCAQF5eDffLVL/fd5C3tF0wJKmZTZTJsamhw4zZl6Rkt+KlgV8x7RCtw+KXATqPiqplrb+rcWnHMkJcUsnd+PUTuV5pI3Y4xenU80rFQDxDrBySY2+nosLywfUUtbkjcyAZK4TBVExkk7PZMQx0AwxsjXvAY6sQHRbbKT1Wd8zfRrbmLAn2w/E7xosxHPMpaswrUcw0CpvNDeMWEFR3JhYcmP0B7qAX/2GWhIg/4Y1ZRZjS284dxTC2VpsdVotpvDF7ROFkOAm6/NZ5MlnML1oyWBYe8QvIJzG1HJhgIQTSrAePxZuoFphS9jUcowc/W3OUMcbzbdea2jjwI3Jlcg/tCEtTzHKL5Ul5WuL7e/T8wQhzOfeQnWZ7ZiGMlMCXOthHm25smvGxg=
```

> Env vars

```bash
export AWS_ACCESS_KEY_ID="ASIA...NSQ"
export AWS_SECRET_ACCESS_KEY="WihcB......PiMeFULn"
export AWS_DEFAULT_REGION="us-east-2"
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2VjEDMaCXV...EAph1DEF8Y="
```

2. Generate AWS boto config file first launch or force it

If you run this script the first time with or without params, it will perform an update of sessions and functions avalaibale by boto first.
```bash
python3 main.py -u
```

3. Start gathering info

> Help

```bash
usage: main.py [-h] [-t THREADS] [-u] [-b [PARAMETER ...]] [-w [PARAMETER ...]] [-p]

Bruteforce AWS rights with boto3

options:
  -h, --help            show this help message and exit
  -t THREADS, --threads THREADS
                        Number of threads to use
  -u, --update-services
                        Update dynamically list of AWS services and associated functions
  -b [PARAMETER ...], --black-list [PARAMETER ...]
                        List of services to remove separated by comma. Launch script with -p to see services
  -w [PARAMETER ...], --white-list [PARAMETER ...]
                        List of services to whitelist/scan separated by comma. Launch script with -p to see services
  -p, --print-services  List of services to whitelist/scan separated by comma
```

Show list of services : 
```bash
python3 main.py -p
```

Generate scan with white-list : 
```bash
python3 main.py -w ec2 sts pricing dynamodb
```

Generate scan with black-list : 
```bash
python3 main.py -b cloudhsm cloudhsmv2 sms dynamodb
```

Generate scan with black-list & white-list (will perform scan on white list without "dynamodb" service): 
```bash
python3 main.py -w ec2 sts pricing dynamodb -b cloudhsm cloudhsmv2 sms dynamodb
```

Total BF (unsafe mode, not recommended if you don't know what you do)
```bash
python3 main.py --unsafe-mode
```

## TBD : 

- [ ] Try to attach logger messages to console


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
