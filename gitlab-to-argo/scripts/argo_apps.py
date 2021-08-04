#!/usr/bin/env python3

"""
Description: An experiment to patch and delete Argo App objects.

NOTES:
kubectl patch app APPNAME  -p '{"metadata": {"finalizers": ["resources-finalizer.argocd.argoproj.io"]}}' --type merge
kubectl delete app APPNAME
"""

from datetime import datetime
import json
import os
import gitlab
import dateutil.parser

g = gitlab.Gitlab(
        gitlab_url,
        private_token=gitlab_token
)


def should_archive_project(project):

        print("Archiving project")


def should_process_project(project):

        valid_cloud_providers = [ "ec2", "crc" ]

        repository_tree = project.repository_tree(all=True)
        engagement_file = [f for f in repository_tree if f["path"] == 'engagement.json']

        if not len(engagement_file) == 1:

                # Engagement file doesn't exist
                print("The Engagement file does not exist!")
                return False

        engagement = json.loads(project.files.get('engagement.json', "master").decode())

        print("Checking Engagement: %s - %s"
        %(engagement.get('customer_name', 'Undefined'),
        engagement.get('project_name', 'Undefined')))

        if not ("launch" in engagement and "launched_date_time" in engagement["launch"]):

                print("Engagement file doesn't have the correct launch data in it")
                return False

        if "archive_date" in engagement:

                try:

                        archive_date_ts = dateutil.parser.parse(engagement["archive_date"]).timestamp()

                except ValueError:

                        print("Could not parse archive date: %s" %engagement["archive_date"])
                        return False

                now_ts = datetime.utcnow().timestamp()

                if now_ts > archive_date_ts:

                        print("Engagement has reached archiving date")
                        #archive_project()


        if not "hosting_environments" in engagement:

                print("Hosting environment is not defined in engagement.json")
                return False

        if len(engagement["hosting_environments"]) == 0:

                print("Hosting environment file is empty")
                return False

        if not "ocp_cloud_provider_name" in engagement["hosting_environments"][0]:

                print("No Cloud Provider name was provided")
                return False

        else:

                cloud_provider = engagement["hosting_environments"][0]["ocp_cloud_provider_name"]


        if not cloud_provider in valid_cloud_providers:

                print("Engagement is using an unsupported Cloud Provider")
                return False

        # :rocket: Ship it!
        return True


def do_not_process(file):

        print(f"Not processing {file}")
        os.remove(file)


if __name__ == "__main__":

        files = [f for f in os.listdir(".")]

        for file in files:

                project_id = file.partition(".")[0] # The project ID is the filename before ".yml"
                project = g.projects.get(project_id, lazy=False)

        if not should_process_project(project):

                do_not_process(file)
