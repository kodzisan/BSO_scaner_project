from gvm.protocols.gmp import Gmp
from argparse import Namespace

def main(gmp: Gmp, args: Namespace):
    tasks = gmp.get_tasks(filter_string="rows=-1")
    for task in tasks.xpath("task"):
        name = task.findtext("name")
        task_id = task.get("id")
        report = task.find("last_report/report")
        report_id = report.get("id") if report is not None else "No report"
        print(f"{name} {task_id} {report_id}")

# gmp i args są przekazywane przez gvm-script
if __name__ == '__gmp__':
    main(globals()["gmp"], globals()["args"])
