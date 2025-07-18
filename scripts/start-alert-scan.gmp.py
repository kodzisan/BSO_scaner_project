# SPDX-FileCopyrightText: 2018 Henning Häcker
# SPDX-FileCopyrightText: 2019-2021 Greenbone AG
#
# SPDX-License-Identifier: GPL-3.0-or-later

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from typing import List

from gvm.protocols.gmp import Gmp

HELP_TEXT = """
        This script makes an E-Mail alert scan.

        Usage examples:
            $ gvm-script --gmp-username name --gmp-password pass ssh --hostname
            ... start-alert-scan.gmp.py +h
            ... start-alert-scan.gmp.py ++target-name ++hosts ++ports \
                    ++port-list-name +C +R +S
            ... start-alert-scan.gmp.py ++target-name ++hosts ++port-list-id \
                    +C ++recipient ++sender
            ... start-alert-scan.gmp.py ++target-id +C ++recipient ++sender
    """

def get_scan_config(gmp: Gmp, config: int, debug: bool = False):
    res = gmp.get_scan_configs(filter_string="rows=-1")

    if config < 0 or config > 5:
        raise ValueError("Wrong config identifier. Choose between [0,5].")

    config_list = [
        "Full and fast",
        "Full and fast ultimate",
        "Full and very deep",
        "Full and very deep ultimate",
        "System Discovery",
        "Base",
    ]

    template_abbreviation_mapper = {
        0: config_list[0],
        1: config_list[1],
        2: config_list[2],
        3: config_list[3],
        4: config_list[4],
        5: config_list[5],
    }

    config_id = None

    for conf in res.xpath("config"):
        cid = conf.xpath("@id")[0]
        name = conf.xpath("name/text()")[0]

        if template_abbreviation_mapper.get(config) == name:
            config_id = cid
            if debug:
                print(name + ": " + config_id)
            break

    if config_id is None:
        raise RuntimeError(f"Scan config '{template_abbreviation_mapper.get(config)}' not found.")

    return config_id


def get_target(
    gmp,
    target_name: str = None,
    hosts: List[str] = None,
    ports: str = None,
    port_list_name: str = None,
    port_list_id: str = None,
    debug: bool = False,
):
    if target_name is None:
        target_name = "target"
    targets = gmp.get_targets(filter_string=target_name)
    existing_targets = [""]
    for target in targets.findall("target"):
        existing_targets.append(str(target.find("name").text))
    counter = 0
    if target_name in existing_targets:
        while True:
            tmp_name = f"{target_name} ({str(counter)})"
            if tmp_name in existing_targets:
                counter += 1
            else:
                target_name = tmp_name
                break

    if debug:
        print(f"target name: {target_name}")

    if not port_list_id:
        existing_port_lists = [""]
        port_lists_tree = gmp.get_port_lists()
        for plist in port_lists_tree.findall("port_list"):
            existing_port_lists.append(str(plist.find("name").text))

        if port_list_name is None:
            port_list_name = "portlist"

        if port_list_name in existing_port_lists:
            counter = 0
            while True:
                tmp_name = f"{port_list_name} ({str(counter)})"
                if tmp_name in existing_port_lists:
                    counter += 1
                else:
                    port_list_name = tmp_name
                    break

        port_list = gmp.create_port_list(name=port_list_name, port_range=ports)
        port_list_id = port_list.xpath("@id")[0]
        if debug:
            print(f"New Portlist-name:\t{port_list_name}")
            print(f"New Portlist-id:  \t{str(port_list_id)}")

    res = gmp.create_target(target_name, hosts=hosts, port_list_id=port_list_id)
    print(f"New target '{target_name}' created.")
    return res.xpath("@id")[0]


def get_alert(
    gmp: Gmp,
    sender_email: str,
    recipient_email: str,
    alert_name: str = None,
    debug: bool = False,
):
    if alert_name is None:
        alert_name = recipient_email

    alerts = gmp.get_alerts(filter_string=f'name={alert_name}')
    existing = alerts.xpath("alert")
    if existing:
        alert_id = existing[0].get("id")
        if debug:
            print(f"[+] Found existing alert '{alert_name}' → {alert_id}")
        return alert_id

    method_data = {
        "message": "Task '$n': $e",
        "notice": "2",
        "from_address": sender_email,
        "subject": "[OpenVAS-Manager] Task",
        "notice_attach_format": "c402cc3e-b531-11e1-9163-406186ea4fc5",
        "to_address": recipient_email,
    }
    res = gmp.create_alert(
        name=alert_name,
        comment="On-demand alert",
        event=gmp.types.AlertEvent.TASK_RUN_STATUS_CHANGED,
        event_data={"status": "Done"},
        condition=gmp.types.AlertCondition.ALWAYS,
        method=gmp.types.AlertMethod.EMAIL,
        method_data=method_data,
    )
    alert_id = res.xpath("@id")[0]
    if debug:
        print(f"[+] Created new alert '{alert_name}' → {alert_id}")
    return alert_id

def get_scanner(gmp: Gmp):
    res = gmp.get_scanners()
    scanner_ids = res.xpath("scanner/@id")
    return scanner_ids[1]


def create_and_start_task(
    gmp: Gmp,
    config_id: str,
    target_id: str,
    scanner_id: str,
    alert_id: str,
    alert_name: str,
    debug: bool = False,
) -> str:
    task_name = f"Alert Scan for Alert1 {alert_name}"
    tasks = gmp.get_tasks(filter_string=f'name="{task_name}"')
    existing_tasks = tasks.findall("task")

    if existing_tasks:
        task_name = f"Alert Scan for Alert {alert_name} ({len(existing_tasks)})"
    task_comment = "Alert Scan"
    res = gmp.create_task(
        name=task_name,
        config_id=config_id,
        target_id=target_id,
        scanner_id=scanner_id,
        alert_ids=[alert_id],
        comment=task_comment,
    )

    task_id = res.xpath("@id")[0]
    gmp.start_task(task_id)

    if debug:
        gmp.stop_task(task_id=task_id)
        print("Task stopped")

    return task_name


def parse_args(args: Namespace):
    parser = ArgumentParser(
        prefix_chars="+",
        add_help=False,
        formatter_class=RawTextHelpFormatter,
        description=HELP_TEXT,
    )

    parser.add_argument(
        "+h",
        "++help",
        action="help",
        help="Show this help message and exit.",
    )

    target = parser.add_mutually_exclusive_group(required=True)

    target.add_argument(
        "++target-id",
        type=str,
        dest="target_id",
        help="Use an existing target by target id",
    )

    target.add_argument(
        "++target-name",
        type=str,
        dest="target_name",
        help="Create a target by name",
    )

    parser.add_argument(
        "++hosts",
        nargs="+",
        dest="hosts",
        help="Host(s) for the new target",
    )

    ports = parser.add_mutually_exclusive_group()

    ports.add_argument(
        "++port-list-id",
        type=str,
        dest="port_list_id",
        help="An existing portlist id for the new target",
    )
    ports.add_argument(
        "++ports",
        type=str,
        dest="ports",
        help="Ports in the new target: e.g. T:80-80,8080",
    )

    parser.add_argument(
        "++port-list-name",
        type=str,
        dest="port_list_name",
        help="Name for the new portlist in the new target",
    )

    config = parser.add_mutually_exclusive_group()

    config.add_argument(
        "+C",
        "++scan-config",
        default=0,
        type=int,
        dest="config",
        help="Choose from existing scan config:"
        "\n  0: Full and fast"
        "\n  1: Full and fast ultimate"
        "\n  2: Full and very deep"
        "\n  3: Full and very deep ultimate"
        "\n  4: System Discovery",
    )

    config.add_argument(
        "++scan-config-id",
        type=str,
        dest="scan_config_id",
        help="Use existing scan config by id",
    )

    parser.add_argument(
        "++scanner-id",
        type=str,
        dest="scanner_id",
        help="Use existing scanner by id",
    )

    parser.add_argument(
        "+R",
        "++recipient",
        required=True,
        dest="recipient_email",
        type=str,
        help="Alert recipient E-Mail address",
    )

    parser.add_argument(
        "+S",
        "++sender",
        required=True,
        dest="sender_email",
        type=str,
        help="Alert senders E-Mail address",
    )

    parser.add_argument(
        "++alert-name",
        dest="alert_name",
        type=str,
        help="Optional Alert name",
    )

    script_args, _ = parser.parse_known_args()
    return script_args


def main(gmp: Gmp, args: Namespace) -> None:
    script_args = parse_args(args)

    if script_args.alert_name is None:
        script_args.alert_name = script_args.recipient_email

    if not script_args.scan_config_id:
        config_id = get_scan_config(gmp, script_args.config)
    else:
        config_id = script_args.scan_config_id

    if not script_args.target_id:
        target_id = get_target(
            gmp,
            target_name=script_args.target_name,
            hosts=script_args.hosts,
            ports=script_args.ports,
            port_list_name=script_args.port_list_name,
            port_list_id=script_args.port_list_id,
        )
    else:
        target_id = script_args.target_id

    alert_id = get_alert(
        gmp,
        script_args.sender_email,
        script_args.recipient_email,
        script_args.alert_name,
    )

    if not script_args.scanner_id:
        scanner_id = get_scanner(gmp)
    else:
        scanner_id = script_args.scanner_id

    task_name = create_and_start_task(
        gmp, config_id, target_id, scanner_id, alert_id, script_args.alert_name
    )

    print(f"Task started: {task_name}\n")
    print("Script finished\n")


if __name__ == "__gmp__":
    main(gmp, args)

