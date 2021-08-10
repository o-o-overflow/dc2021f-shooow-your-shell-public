#!/usr/bin/env python3
import subprocess
import argparse
import logging
import time
import sys
import ast
import os
import re

#pylint:disable=logging-format-interpolation,logging-fstring-interpolation

GAME_NAME = 'shooow-your-shell'

l = logging.getLogger("ooows-flagbot")

HISTORY_FILE = "/history.txt"
LOCAL_HISTORY_FILE = f"./{HISTORY_FILE}"
LOCAL_HISTORY_FILE_TMP = f"./{HISTORY_FILE}.tmp"

def kube_exec(namespace, pod_name, cmd):
    base = KUBE_BASE_CMD + ["exec", "-i", "-n", namespace, pod_name, "--"]
    full_cmd = base + cmd
    result = subprocess.run(full_cmd, universal_newlines=True, stdout=subprocess.PIPE, check=False)
    l.debug(" ".join(full_cmd))
    if result.returncode == 0:
        return True
    else:
        # notify only b/c likely reason for fail is restarting of depot
        l.error(f"Kube command exec failed {namespace}:{pod_name} --> {cmd}")
        l.debug(" ".join(full_cmd))
        return False

def kube_cp(ffrom, fto, doprint=False):
    full_cmd = KUBE_BASE_CMD + ["cp", ffrom, fto]

    result = subprocess.run(full_cmd, universal_newlines=True, stdout=subprocess.PIPE, check=False)
    if doprint:
        l.debug(" ".join(full_cmd))
    if result.returncode == 0:
        return True
    else:
        # notify only b/c likely reason for fail is restarting of depot
        l.error(f"copy {ffrom=} {fto=} failed")
        l.debug(" ".join(full_cmd))
        return False

def async_kube_cp(ffrom, fto, doprint=False): #pylint:disable=unused-argument
    full_cmd = KUBE_BASE_CMD + ["cp", ffrom, fto]

    result = subprocess.Popen(full_cmd, universal_newlines=True, stdout=subprocess.PIPE) #pylint:disable=consider-using-with
    l.debug(" ".join(full_cmd))
    return {"proc": result, "cmd":full_cmd}

def get_all_pod_info(kubeconfig, name):
    get_service_pod = ["kubectl", "get", "pods", "--all-namespaces", "--insecure-skip-tls-verify", "--kubeconfig",
                       kubeconfig,
                       "--no-headers=true", "-o", "go-template", "--template",
                       "'{{range .items}}{{.metadata.namespace}}{{\" \"}}{{.metadata.name}}{{\"\\n\"}}{{end}}'"]


    to_return = []
    process = subprocess.Popen(get_service_pod, stdout=subprocess.PIPE, universal_newlines=True) #pylint:disable=consider-using-with
    for line in iter(process.stdout.readline,''):
        if len(line) < 3:
            continue
        #line = line.decode('utf-8')
        line = line.replace("'","")
        namespace, pod_name = line.split(" ")
        namespace = namespace.strip()
        pod_name = pod_name.strip()

        if not pod_name.startswith(name):
            continue

        #_log.debug(line)
        to_return.append((namespace, pod_name))

    return to_return

def main(kubeconfig):
    l.info(f"Start bot with {kubeconfig=} at time {time.time()}")
    while True:

        if os.path.exists("/tmp/pause"):
            l.info("Pausing due to presence of /tmp/pause...")
            time.sleep(5)

        team_pods = get_all_pod_info(kubeconfig, GAME_NAME)
        team_id_to_pod = {}
        for ns, pod_name in team_pods:
            match = re.search(r'team-(\d+)-', pod_name)
            team_id = int(match.group(1))
            if team_id == 17:
                continue
            team_id_to_pod[team_id] = (ns, pod_name)

        if len(team_id_to_pod.keys()) != 16:
            l.error(f"WTF: {team_pods=}\n{team_id_to_pod.keys()=}")
            return

        # get all the histories!
        valid_histories = [ ]
        for i in range(1, 17):
            game_ns, game_name = team_id_to_pod[i]
            res = kube_cp(f"{game_ns}/{game_name}:{HISTORY_FILE}", LOCAL_HISTORY_FILE_TMP)
            if not res:
                l.info(f"Couldn't get history.txt from team {i}, skipping them.")
                continue

            # Validate the local history tmp we just copied
            with open(LOCAL_HISTORY_FILE_TMP, 'r') as f:
                content = f.read()
                try:
                    history = ast.literal_eval(content)
                    assert all(set(a.keys()) == { 'team', 'code', 'time', 'blocked', 'winner' } for a in history)
                    assert all(type(a['team']) is str for a in history)
                    assert all(type(a['time']) is float for a in history)
                    assert all(type(a['code']) is bytes for a in history)
                    assert all(type(a['blocked']) is set for a in history)
                    assert all(type(a['winner']) is bool for a in history)
                except Exception as e: #pylint:disable=broad-except
                    l.error(f"Unable to parse {content=} from team {i}, skipping {e=}")
                    continue

            # skip empty histories
            if not history:
                continue

            valid_histories.append((history,i))

        del i

        # skip when there's nothing to sync
        if not valid_histories:
            continue

        latest_history, latest_team = sorted(valid_histories, key=lambda h: h[0][-1]['time'])[-1]
        with open(LOCAL_HISTORY_FILE, 'w') as dst:
            dst.write(str(latest_history))

        # If history correct, push it to every other team
        results = []
        for j in range(1, 17):
            if j == latest_team:
                l.info(f"skipping recopying {j} to {latest_team}")
                continue
            game_ns, game_name = team_id_to_pod[j]
            l.info(f"{game_ns=} {game_name=}")
            res = async_kube_cp(LOCAL_HISTORY_FILE, f"{game_ns}/{game_name}:{HISTORY_FILE}")
            results.append(res)

        for res in results:
            try:
                res["proc"].wait(timeout=5)
                l.debug(f"Completed {res['cmd']}, {res['proc'].returncode}")
                if res["proc"].returncode != 0:
                    l.error(f"IS THIS BAD? LOOK INTO IT: Couldn't SET history.txt from team {latest_team}.")
            except subprocess.TimeoutExpired:
                l.error(f"Timeout expired while waiting for {res['cmd']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="ooows-flagbot")
    parser.add_argument("--kubeconfig", help="The location of the kubernetes config")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--version", action="version", version="%(prog)s v0.0.1")

    args = parser.parse_args()

    _kubeconfig = None
    if args.kubeconfig:
        _kubeconfig = args.kubeconfig
    elif 'KUBECONFIG' in os.environ:
        _kubeconfig = os.environ['KUBECONFIG']

    if not _kubeconfig:
        l.error("Error, must specify a kubernetes config")
        parser.print_help()
        sys.exit(1)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    KUBE_BASE_CMD = ["kubectl", "--insecure-skip-tls-verify", "--kubeconfig", _kubeconfig]
    l.info("Starting shooow-your-shell-syncer bot....")
    main(_kubeconfig)
