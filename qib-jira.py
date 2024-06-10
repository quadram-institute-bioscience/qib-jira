#!/usr/bin/env python3
import argparse
import re
from dotenv import load_dotenv
import os
import sys
from jira import JIRA
from datetime import datetime, timedelta
import sqlite3
import hashlib
import schedule
import requests
import logging

load_dotenv()
JIRA_TOKEN = os.getenv("JIRA_TOKEN")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
HEALTH_CHECK_URL = os.getenv("HEALTH_CHECK_URL")


# logging.basicConfig()
# schedule_logger = logging.getLogger('schedule')
# schedule_logger.setLevel(level=logging.INFO)


def health_check(health_check_url, timeout=10):
    """
    Makes a GET request to the specified health check URL with a given timeout.

    Args:
        health_check_url (str): The URL to perform the health check.
        timeout (int, optional): The timeout in seconds for the request. Defaults to 10.

    Returns:
        None

    Raises:
        requests.RequestException: If an error occurs during the request.

    """
    try:
        requests.get(health_check_url, timeout=timeout)
        logging.info(f"Pinged health check: {health_check_url}")
    except requests.RequestException as e:
        logging.error(e)


def valid_key(pattern, key):
    """
    Validates if a given key matches the pattern of a valid JIRA issue key.

    Args:
        pattern (str): The regular expression pattern to match against the key.
        key (str): The key to be validated.

    Raises:
        ValueError: If the key does not match the pattern.

    Returns:
        str: The validated key.

    """
    if not re.match(pattern, key):
        raise ValueError(f"{key} is not a valid JIRA issue key")
    return key


def calculate_md5(*args):
    """
    Calculates the MD5 hash of the given arguments.

    Args:
        *args: Variable length arguments to be hashed.

    Returns:
        str: The MD5 hash of the concatenated string representation of the arguments.
    """
    m = hashlib.md5()
    for arg in args:
        if arg is not None:
            m.update(str(arg).encode("utf-8"))
    return m.hexdigest()


def update(database_location, days, project, email, token, health_check_url=None):
    """
    Updates the database with issues from JIRA based on the given parameters.

    Args:
        database_location (str): The location of the SQLite database.
        days (int): The number of days from today to calculate the date.
        project (str): The project key to filter the issues.
        email (str): The JIRA email.
        token (str): The JIRA token.

    Raises:
        ValueError: If the JIRA email or token is not provided.

    Returns:
        None

    """
    if email is None or token is None:
        raise ValueError("Jira email and token are required")
    jira = JIRA(
        server="https://quadram-institute.atlassian.net",
        basic_auth=(email, token),
    )
    logging.info(f"Health check: {HEALTH_CHECK_URL}")
    # bsup = jira.project(project)

    # Calculate the date n days from today
    one_month_ago = datetime.now() - timedelta(days=days)
    one_month_ago_str = one_month_ago.strftime("%Y-%m-%d")

    # Define JQL query to fetch issues created or updated after one month ago
    jql_query = f"createdDate >= '{one_month_ago_str}' AND updated >= '{one_month_ago_str}' AND project={project}"
    # jql_query = f"project={project}"

    # Define fields to retrieve
    # fields = [
    #     'summary', 'key', 'id', 'parent', 'issuetype', 'status',
    #     'project', 'priority', 'resolution', 'assignee', 'reporter',
    #     'creator', 'created', 'updated', 'lastViewed', 'resolved',
    #     'duedate', 'votes', 'labels', 'description', 'environment'
    # ]

    max_results = 100
    start_at = 0
    logging.info("Starting...")

    # Create a SQLite database connection
    conn = sqlite3.connect(database_location)
    c = conn.cursor()
    # Create table
    c.execute("""
        CREATE TABLE IF NOT EXISTS issues (
            assignee TEXT,
            assignee_id TEXT,
            created TEXT,
            creator TEXT,
            description TEXT,
            due_date TEXT,
            environment TEXT,
            issue_type TEXT,
            issue_key TEXT,
            issue_id TEXT,
            labels TEXT,
            last_viewed TEXT,
            priority TEXT,
            project TEXT,
            reporter TEXT,
            resolution TEXT,
            resolution_date TEXT,
            status TEXT,
            summary TEXT,
            updated TEXT,
            original_estimate TEXT,
            remaining_estimate TEXT,
            worklog TEXT,
            time_tracking TEXT,
            isp TEXT,
            md5_hash TEXT
        )
    """)
    try:
        while True:
            print(f"Fetching issues from {start_at} to {start_at + max_results}")
            issues = jira.search_issues(
                jql_query, startAt=start_at, maxResults=max_results
            )

            # Print fetched data
            for issue in issues:
                # print("Assignee:", issue.fields.assignee.displayName if issue.fields.assignee else None)
                # print("Assignee ID:", issue.fields.assignee.accountId if issue.fields.assignee else None)
                # print("Created:", issue.fields.created)
                # print("Creator:", issue.fields.creator)
                # print("Description:", issue.fields.description)
                # print("Due Date:", issue.fields.duedate)
                # print("Environment:", issue.fields.environment)
                # print("Issue Key:", issue.key)
                # print("Issue ID:", issue.fields.issuetype.id)
                # print("Issue Type:", issue.fields.issuetype.name)
                # print("Labels:", issue.fields.labels)
                # print("Last Viewed:", issue.fields.lastViewed)
                # print("Priority:", issue.fields.priority.name)
                # print("Project:", issue.fields.project.key)
                # print("Reporter:", issue.fields.reporter)
                # print("Resolution:", issue.fields.resolution.name if issue.fields.resolution else None)
                # print("Resolution Date:", issue.fields.resolutiondate)
                # print("Status:", issue.fields.status.name)
                # print("Summary:", issue.fields.summary)
                # print("Updated:", issue.fields.updated)
                # print("Σ Original_Estimate:", issue.fields.aggregatetimeoriginalestimate)
                # print("Original_Estimate:", issue.fields.timeoriginalestimate)
                # print("Remaining_Estimate:", issue.fields.aggregatetimeestimate)
                # print("Worklog:", [f"{x.timeSpent}|started:({(x.started)})" for x in issue.fields.worklog.worklogs if len(issue.fields.worklog.worklogs) > 0])
                # print("Time Tracking:", issue.fields.timetracking.raw.get('timeSpent', None) if issue.fields.timetracking.raw else None)
                # print(f"ISP: {issue.fields.customfield_10065}")
                # print(f"Participants: {issue.fields.customfield_10035}")
                # print("==="*20)

                # Prepare data
                data = (
                    issue.fields.assignee.displayName
                    if issue.fields.assignee
                    else None,
                    issue.fields.assignee.accountId if issue.fields.assignee else None,
                    issue.fields.created,
                    issue.fields.creator.displayName if issue.fields.creator else None,
                    issue.fields.description,
                    issue.fields.duedate,
                    issue.fields.environment,
                    issue.fields.issuetype.name,
                    issue.key,
                    issue.fields.issuetype.id,
                    ", ".join(issue.fields.labels),
                    issue.fields.lastViewed,
                    issue.fields.priority.name,
                    issue.fields.project.key,
                    issue.fields.reporter.displayName
                    if issue.fields.reporter
                    else None,
                    issue.fields.resolution.name if issue.fields.resolution else None,
                    issue.fields.resolutiondate,
                    issue.fields.status.name,
                    issue.fields.summary,
                    issue.fields.updated,
                    issue.fields.timeoriginalestimate,
                    issue.fields.aggregatetimeestimate,
                    ", ".join(
                        [
                            f"{x.timeSpent}|started:({(x.started)})"
                            for x in issue.fields.worklog.worklogs
                            if len(issue.fields.worklog.worklogs) > 0
                        ]
                    ),
                    issue.fields.timetracking.raw.get("timeSpent", None)
                    if issue.fields.timetracking.raw
                    else None,
                    str(issue.fields.customfield_10065),
                )
                num_columns = len(data) + 1  # Add 1 for md5_hash
                placeholders = ["?"] * num_columns
                # Calculate md5 hash of the data
                md5_hash = calculate_md5(*data)
                # Check if a record with the same hash already exists
                c.execute("SELECT * FROM issues WHERE md5_hash = ? ", (md5_hash,))
                if c.fetchone() is None:
                    c.execute("SELECT * FROM issues WHERE issue_key = ? ", (issue.key,))
                    if c.fetchone() is None:
                        logging.info(f"Inserting issue: {issue.key}")
                        # Insert data into database
                        c.execute(
                            f"""INSERT INTO issues VALUES
                        ({",".join(placeholders)})""",
                            data + (md5_hash,),
                        )
                    else:
                        logging.info(f"Updating issue: {issue.key}")
                        c.execute(
                            """
                                UPDATE issues
                                SET assignee = ?, assignee_id = ?,created = ?, creator = ?, description = ?, due_date = ?, environment = ?, issue_type = ?, issue_key = ?, issue_id = ?, labels = ?, last_viewed = ?, priority = ?, project = ?, reporter = ?, resolution = ?, resolution_date = ?, status = ?, summary = ?, updated = ?, original_estimate = ?, remaining_estimate = ?, worklog = ?, time_tracking = ?, isp = ?, md5_hash = ?
                                WHERE issue_key = ?
                            """,
                            data + (md5_hash, issue.key),
                        )

            # Find custom fields
            # fields = jira.fields()
            # # Make a map from field name -> field id
            # nameMap = {field['name']:field['id'] for field in fields}

            # for k,v in nameMap.items():
            #     if "participants" in k.lower():
            #         print(f"{k}:{v}")

            if len(issues) < max_results:
                break
            start_at += max_results

        # Commit changes and close connection
        conn.commit()
        conn.close()
        logging.info("Completed!")
        health_check(HEALTH_CHECK_URL)
    except Exception as e:
        logging.error(e)


def main():
    """
    This function parses the command line arguments and calls the update function to update the JIRA issues in the database.
    """
    # Create an argument parser
    parser = argparse.ArgumentParser(
        description="Download records from Cloud JIRA to a local sqlite database",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    # Add arguments to the parser
    parser.add_argument(
        "--email", type=str, default=None, help="JIRA Cloud Admin Email"
    )
    parser.add_argument("--token", type=str, default=None, help="JIRA Cloud API Token")
    parser.add_argument(
        "--database",
        type=str,
        default="qib-jira.db",
        help="Location of the database file",
    )
    parser.add_argument("--project", type=str, default="BSUP", help="Project name")
    parser.add_argument("--days", type=int, default=30, help="Number of days to query")
    parser.add_argument(
        "--schedule",
        type=int,
        default=None,
        help="Run this script as a cron job every X minutes",
    )
    parser.add_argument(
        "--health-check",
        type=str,
        default=None,
        help="Provide a health check URL to perform a health check if you run this script as a scheduled job",
    )

    # Parse the command line arguments
    args = parser.parse_args()

    # Check if email and token are provided
    if args.email is None or args.token is None:
        # Check if environment variables are set
        if os.getenv("JIRA_EMAIL") is None or os.getenv("JIRA_TOKEN") is None:
            # If not, exit the program with an error message
            sys.exit(
                "email and token were not provided. The env variables JIRA_EMAIL and JIRA_TOKEN environment variables were not set either!"
            )
        else:
            # If environment variables are set, use them
            args.email = os.getenv("JIRA_EMAIL")
            args.token = os.getenv("JIRA_TOKEN")
    logging.info(f"Using email: {args.email}")
    global HEALTH_CHECK_URL
    if args.health_check:
        HEALTH_CHECK_URL = args.health_check

    if args.schedule:
        logging.info(f"Running the script every {args.schedule} minutes")
        schedule.every(args.schedule).minutes.do(
            update,
            database_location=args.database,
            days=args.days,
            project=args.project,
            email=args.email,
            token=args.token,
            health_check_url=HEALTH_CHECK_URL,
        )
        while True:
            schedule.run_pending()
    else:
        logging.info(f"Running the script for {args.days} days")
        # Call the update function with the parsed arguments
        update(
            args.database,
            args.days,
            args.project,
            args.email,
            args.token,
            HEALTH_CHECK_URL,
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(lineno)d - %(message)s"
    )
    logging.info("Starting qib-jira.py")
    main()
