#!/usr/bin/env python
import argparse
import os
import sys
from datetime import datetime
from datetime import timedelta
from random import randint
from subprocess import Popen, DEVNULL

def main(def_args=sys.argv[1:]):
    args = arguments(def_args)
    curr_date = datetime.now()
    
    if args.repository is not None:
        start = args.repository.rfind('/') + 1
        end = args.repository.rfind('.')
        directory = args.repository[start:end]
    else:
        directory = 'repository-' + curr_date.strftime('%Y-%m-%d-%H-%M-%S')

    if os.path.exists(directory):
        print(f"(!) Folder '{directory}' sudah ada. Menggunakan folder tersebut.")
    else:
        os.mkdir(directory)
    
    os.chdir(directory)
    
    print("(*) Menginisialisasi Repository Git...")
    run(['git', 'init', '-b', 'main'])

    if args.user_name is not None:
        run(['git', 'config', 'user.name', args.user_name])

    if args.user_email is not None:
        run(['git', 'config', 'user.email', args.user_email])

    days_before = args.days_before
    days_after = args.days_after
    if days_before < 0 or days_after < 0:
        sys.exit('days_before dan days_after tidak boleh negatif')

    start_date = curr_date.replace(hour=20, minute=0) - timedelta(days_before)
    total_days = days_before + days_after
    
    print(f"(*) Memulai proses untuk {total_days} hari ke belakang...")
    print("(*) Mohon tunggu, proses ini memakan waktu...")

    commit_count = 0
    for i, day in enumerate(start_date + timedelta(n) for n in range(total_days)):
        percentage = (i / total_days) * 100
        print(f"\rProcess: {percentage:.1f}% | Date: {day.strftime('%Y-%m-%d')} | Commits: {commit_count}", end='')
        
        if (not args.no_weekends or day.weekday() < 5) and randint(0, 100) < args.frequency:
            for commit_time in (day + timedelta(minutes=m) for m in range(contributions_per_day(args))):
                contribute(commit_time)
                commit_count += 1

    print("\n\n(*) Generate commit selesai. Sekarang mencoba push ke GitHub...")

    if args.repository is not None:
        run(['git', 'remote', 'remove', 'origin']) 
        run(['git', 'remote', 'add', 'origin', args.repository])
        run(['git', 'branch', '-M', 'main'])
        
        try:
            p = Popen(['git', 'push', '-u', 'origin', 'main'])
            p.wait()
        except KeyboardInterrupt:
            print("\nPush dibatalkan user.")
            sys.exit()

    print('\n\x1b[6;30;42mSUKSES! Silakan cek profil GitHub kamu.\x1b[0m')

def contribute(date):
    with open(os.path.join(os.getcwd(), 'README.md'), 'a') as file:
        file.write(message(date) + '\n\n')
    run(['git', 'add', '.'])
    run(['git', 'commit', '-q', '-m', '"%s"' % message(date),
         '--date', date.strftime('"%Y-%m-%d %H:%M:%S"')])

def run(commands):
    Popen(commands, stdout=DEVNULL, stderr=DEVNULL).wait()

def message(date):
    return date.strftime('Contribution: %Y-%m-%d %H:%M')

def contributions_per_day(args):
    max_c = args.max_commits
    if max_c > 20: max_c = 20
    if max_c < 1: max_c = 1
    return randint(1, max_c)

def arguments(argsval):
    parser = argparse.ArgumentParser()
    parser.add_argument('-nw', '--no_weekends', required=False, action='store_true', default=False, help="do not commit on weekends")
    parser.add_argument('-mc', '--max_commits', type=int, default=10, required=False, help="max commits per day")
    parser.add_argument('-fr', '--frequency', type=int, default=80, required=False, help="percentage of days to commit")
    parser.add_argument('-r', '--repository', type=str, required=False, help="remote repository link")
    parser.add_argument('-un', '--user_name', type=str, required=False, help="git config user.name")
    parser.add_argument('-ue', '--user_email', type=str, required=False, help="git config user.email")
    parser.add_argument('-db', '--days_before', type=int, default=365, required=False, help="days before to start")
    parser.add_argument('-da', '--days_after', type=int, default=0, required=False, help="days after to end")
    return parser.parse_args(argsval)

if __name__ == "__main__":
    main()