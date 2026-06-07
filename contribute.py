#!/usr/bin/env python3

import argparse
import os
import sys
import logging
from datetime import datetime, timedelta
from pathlib import Path
from random import randint, gauss
from subprocess import Popen, PIPE, DEVNULL
from typing import Optional

COMMIT_LOG_FILE  = "commits.txt"
MAX_COMMITS_CAP  = 20
MIN_COMMITS_CAP  = 1
DEFAULT_COMMITS  = 10
DEFAULT_FREQ     = 80
DEFAULT_DAYS_BEF = 365
DEFAULT_DAYS_AFT = 0
COMMIT_HOUR      = 20  

def setup_logger() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-8s  %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger("gh-activity")

log = setup_logger()

def git_run(args: list[str], capture: bool = False) -> tuple[int, str, str]:
    try:
        proc = Popen(
            args,
            stdout=PIPE if capture else DEVNULL,
            stderr=PIPE if capture else DEVNULL,
        )
        stdout, stderr = proc.communicate()
        return (
            proc.returncode,
            stdout.decode().strip() if stdout else "",
            stderr.decode().strip() if stderr else "",
        )
    except FileNotFoundError:
        log.error("Git gak nemu di sistem nih. Install dulu gih di https://git-scm.com")
        sys.exit(1)


def git_is_available() -> bool:
    code, _, _ = git_run(["git", "--version"], capture=True)
    return code == 0


def git_init(branch: str = "main") -> None:
    code, _, _ = git_run(["git", "init", "-b", branch], capture=True)
    if code != 0:
        git_run(["git", "init"], capture=True)
        git_run(["git", "checkout", "-b", branch], capture=True)


def git_configure(user_name: Optional[str], user_email: Optional[str]) -> None:
    if user_name:
        git_run(["git", "config", "user.name", user_name])
    if user_email:
        git_run(["git", "config", "user.email", user_email])

def prepare_directory(directory: str) -> None:
    path = Path(directory)
    if path.exists():
        log.info(f"Folder '{directory}' udah ada — langsung kita pake aja ya.")
    else:
        try:
            path.mkdir(parents=True)
            log.info(f"Folder '{directory}' mantap, berhasil dibuat!")
        except OSError as exc:
            log.error(f"Waduh, gagal bikin folder gara-gara: {exc}")
            sys.exit(1)
    os.chdir(directory)


def init_commit_log() -> None:
    log_path = Path(COMMIT_LOG_FILE)
    if not log_path.exists():
        log_path.write_text("# GitHub Activity Generator — Commit Log\n\n", encoding="utf-8")
    git_run(["git", "add", COMMIT_LOG_FILE])
    git_run(["git", "commit", "-m", "init: create contribution log"])
    log.info(f"Beres! '{COMMIT_LOG_FILE}' udah dibikin sekalian commit pertama.")


def setup_repository(directory: str, args: argparse.Namespace) -> None:
    prepare_directory(directory)
    git_init()
    git_configure(args.user_name, args.user_email)
    init_commit_log()

def commit_message(date: datetime) -> str:
    return date.strftime("Contribution: %Y-%m-%d %H:%M")


def commits_for_day(max_commits: int) -> int:
    max_c = min(max(max_commits, MIN_COMMITS_CAP), MAX_COMMITS_CAP)
    sample = int(abs(gauss(max_c / 2, max_c / 4))) + 1
    return max(MIN_COMMITS_CAP, min(sample, max_c))


def make_commit(date: datetime) -> bool:
    log_path = Path(os.getcwd()) / COMMIT_LOG_FILE
    try:
        with open(log_path, "a", encoding="utf-8") as fh:
            fh.write(commit_message(date) + "\n")
    except IOError as exc:
        log.warning(f"Gagal nulis log nih: {exc}")
        return False

    code, _, err = git_run(["git", "add", COMMIT_LOG_FILE], capture=True)
    if code != 0:
        log.warning(f"git add gagal cuy: {err}")
        return False

    code, _, err = git_run(
        [
            "git", "commit", "-q",
            "-m", commit_message(date),
            "--date", date.strftime("%Y-%m-%d %H:%M:%S"),
        ],
        capture=True,
    )
    if code != 0:
        log.warning(f"git commit gagal: {err}")
        return False

    return True

def push_to_remote(repository: str) -> bool:
    log.info("Lagi nyetting remote origin dulu…")
    git_run(["git", "remote", "remove", "origin"], capture=True)

    code, _, err = git_run(["git", "remote", "add", "origin", repository], capture=True)
    if code != 0:
        log.error(f"Gagal nambahin remote: {err}")
        return False

    git_run(["git", "branch", "-M", "main"])
    log.info("Otw nge-push commit ke GitHub lu…")

    try:
        proc = Popen(["git", "push", "-u", "origin", "main"])
        proc.wait()
        if proc.returncode != 0:
            log.error("Waduh, push-nya gagal. Pastikan SSH/token lu udah bener dan reponya emang ada.")
            return False
        return True
    except KeyboardInterrupt:
        log.warning("Push dibatalin ama user.")
        sys.exit(0)

def print_progress(current: int, total: int, commits: int, date: datetime) -> None:
    bar_len  = 35
    filled   = int(bar_len * current / total)
    bar      = "█" * filled + "░" * (bar_len - filled)
    percent  = current / total * 100
    print(
        f"\r  [{bar}] {percent:5.1f}%  |  "
        f"{date.strftime('%Y-%m-%d')}  |  "
        f"{commits:>5} commit",
        end="",
        flush=True,
    )


def print_summary(commit_count: int, skipped: int, directory: str, repository: Optional[str]) -> None:
    print("\n")
    print("─" * 60)
    print(f"  ✅  Total commit yang sukses dibikin : {commit_count}")
    print(f"  ⏭️   Hari yang dilewati (skip)        : {skipped}")
    print(f"  📁  Lokasi folder lokal              : {directory}")
    if not repository:
        print()
        print("  Belum nyambung ke remote? Gini cara manualnya:")
        print(f"    cd {directory}")
        print("    git remote add origin <URL_REPO_LU>")
        print("    git push -u origin main")
    print("─" * 60)

def generate_activity(args: argparse.Namespace) -> None:
    now        = datetime.now()
    directory  = _resolve_directory(args.repository, now)
    origin_dir = os.getcwd()

    if args.days_before < 0 or args.days_after < 0:
        log.error("days_before ama days_after gak boleh minus dong.")
        sys.exit(1)

    setup_repository(directory, args)

    start_date = now.replace(
        hour=COMMIT_HOUR, minute=0, second=0, microsecond=0
    ) - timedelta(days=args.days_before)
    total_days = args.days_before + args.days_after
    end_date   = start_date + timedelta(days=total_days)

    print()
    log.info(f"Rentang tanggal : {start_date.strftime('%Y-%m-%d')} → {end_date.strftime('%Y-%m-%d')}")
    log.info(f"Frekuensi       : {args.frequency}% hari aktif")
    log.info(f"Max commit/hari : {min(args.max_commits, MAX_COMMITS_CAP)}")
    log.info(f"Libur weekend   : {'Yo’i, kaum rebahan' if args.no_weekends else 'Hajar terus, gas pol!'}")
    log.info(f"File log        : {COMMIT_LOG_FILE} (README.md aman gak diotak-atik)")
    print()

    commit_count = 0
    skipped_days = 0

    for i in range(total_days):
        day = start_date + timedelta(days=i)
        print_progress(i + 1, total_days, commit_count, day)

        if args.no_weekends and day.weekday() >= 5:
            skipped_days += 1
            continue

        if randint(0, 100) >= args.frequency:
            continue

        n = commits_for_day(args.max_commits)
        for j in range(n):
            commit_time = day + timedelta(minutes=j * randint(5, 30))
            if make_commit(commit_time):
                commit_count += 1

    print_summary(commit_count, skipped_days, directory, args.repository)

    if args.repository:
        success = push_to_remote(args.repository)
        if success:
            print("\n  🎉  MANTAP, BERHASIL! Buruan cek contribution graph GitHub lu, auto ijo-ijo!\n")
        else:
            print(f"\n  ⚠️   Commit udah aman di folder '{directory}', tapi pas nyoba push malah gagal.")
            print("       Coba push manual aja deh:\n")
            print(f"       cd {directory} && git push -u origin main\n")

    os.chdir(origin_dir)


def _resolve_directory(repository: Optional[str], now: datetime) -> str:
    if repository:
        start = repository.rfind("/") + 1
        end   = repository.rfind(".")
        name  = repository[start:] if end == -1 else repository[start:end]
        return name or f"repo-{now.strftime('%Y%m%d-%H%M%S')}"
    return f"repository-{now.strftime('%Y-%m-%d-%H-%M-%S')}"

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="github_activity_generator.py",
        description=(
            "╔══════════════════════════════════════════╗\n"
            "║   GitHub Activity Generator              ║\n"
            "╚══════════════════════════════════════════╝\n"
            "\n⚠️  Disclaimer: Buat seru-seruan ama belajar doang ya, jangan disalahgunakan!"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "──────────────────────────────────────────────\n"
            "  Contoh Penggunaan:\n"
            "\n"
            "  # Standar — langsung push ke repo GitHub\n"
            "  python github_activity_generator.py \\\n"
            "      -r git@github.com:username/my-repo.git\n"
            "\n"
            "  # Biar keliatan natural — weekend libur, 60%% aktif, maks 8 commit/hari\n"
            "  python github_activity_generator.py \\\n"
            "      -r git@github.com:username/my-repo.git \\\n"
            "      -nw -fr 60 -mc 8\n"
            "\n"
            "  # Cuma generate di lokal aja (tanpa push)\n"
            "  python github_activity_generator.py -db 180 -nw\n"
            "──────────────────────────────────────────────"
        ),
    )

    repo_group = parser.add_argument_group("🔗  Repository")
    repo_group.add_argument(
        "-r", "--repository",
        type=str,
        default=None,
        metavar="URL",
        help="Link repo GitHub lu (bisa SSH atau HTTPS). Kalo dikosongin, cuma generate di lokal doang.",
    )

    id_group = parser.add_argument_group("👤  Identitas Git")
    id_group.add_argument(
        "-un", "--user_name",
        type=str,
        default=None,
        metavar="NAME",
        help="Nama buat git config user.name (opsional).",
    )
    id_group.add_argument(
        "-ue", "--user_email",
        type=str,
        default=None,
        metavar="EMAIL",
        help="Email buat git config user.email (opsional).",
    )

    commit_group = parser.add_argument_group("⚙️   Pengaturan Commit")
    commit_group.add_argument(
        "-mc", "--max_commits",
        type=int,
        default=DEFAULT_COMMITS,
        metavar="N",
        help=f"Maksimal commit per hari (1–{MAX_COMMITS_CAP}). Default: {DEFAULT_COMMITS}.",
    )
    commit_group.add_argument(
        "-fr", "--frequency",
        type=int,
        default=DEFAULT_FREQ,
        metavar="PCT",
        help=f"Persentase hari aktif commit (0–100). Default: {DEFAULT_FREQ}.",
    )
    commit_group.add_argument(
        "-nw", "--no_weekends",
        action="store_true",
        default=False,
        help="Skip hari Sabtu & Minggu (biar keliatan kayak manusia normal, gak keliatan bot bgt).",
    )

    date_group = parser.add_argument_group("📅  Rentang Waktu")
    date_group.add_argument(
        "-db", "--days_before",
        type=int,
        default=DEFAULT_DAYS_BEF,
        metavar="DAYS",
        help=f"Mundur berapa hari ke belakang dari hari ini. Default: {DEFAULT_DAYS_BEF}.",
    )
    date_group.add_argument(
        "-da", "--days_after",
        type=int,
        default=DEFAULT_DAYS_AFT,
        metavar="DAYS",
        help=f"Maju berapa hari ke depan dari hari ini. Default: {DEFAULT_DAYS_AFT}.",
    )

    return parser

def main(argv: list[str] = sys.argv[1:]) -> None:
    parser = build_parser()
    args   = parser.parse_args(argv)

    if not git_is_available():
        log.error("Git gak terdeteksi nih. Install dulu gih: https://git-scm.com")
        sys.exit(1)

    print(
        "\n"
        "╔══════════════════════════════════════════╗\n"
        "║   GitHub Activity Generator              ║\n"
        "╚══════════════════════════════════════════╝\n"
    )

    generate_activity(args)


if __name__ == "__main__":
    main()
