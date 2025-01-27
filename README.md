## General

This project has been released because, impossible to find robust library for brute forcing AWS IAM rights.

Tested thos two projects but does not output same results... : 
https://github.com/andresriancho/enumerate-iam
https://github.com/carlospolop/bf-aws-permissions


## Information

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

