#!/usr/bin/env python3

import argparse
import boto3
import datetime

class GetCostPerUser():
    """
        Method to get the AWS cost details per user
        1. Create a TAG for each resource consumption and assign it to the resource created
        2. Execute the script to get the TSV generated

        python get_cost_per_user.py --days=10 > filename.tsv
    """
    def __init__(self):
        self.cost_explorer = None
        parser = argparse.ArgumentParser()
        parser.add_argument('--days', type=int, default=30)
        self.args = parser.parse_args()

        now = datetime.datetime.utcnow()
        self.start = (now - datetime.timedelta(days=self.args.days)).strftime('%Y-%m-%d')
        self.end = now.strftime('%Y-%m-%d')

    def create_session_for_cost_explorer(self):
        """
            Creates a boto session for cost 
        """
        session = boto3.session.Session()
        self.cost_explorer = session.client('ce')

    def get_result(self):
        """
            Gets the result from Cost Explorer
        """
        results = []
        token = None
        while True:
            if token:
                kwargs = {'NextPageToken': token}
            else:
                kwargs = {}
                data = self.cost_explorer.get_cost_and_usage(TimePeriod={'Start': self.start, 'End':  self.end}, Granularity='DAILY', Metrics=['UnblendedCost'], GroupBy=[{'Type': 'TAG', 'Key': 'username'},{'Type': 'DIMENSION', 'Key': 'LINKED_ACCOUNT'}],**kwargs)
                results += data['ResultsByTime']
                token = data.get('NextPageToken')
                if not token:
                    break
        return results

    def generate_csv(self, details: dict):
        """
            Generate the CSV for cost details
        """
        print('\t'.join(['TimePeriod', 'Name','LinkedAccount', 'Amount', 'Unit', 'Estimated']))
        for result_by_time in details:
            for group in result_by_time['Groups']:
                amount = group['Metrics']['UnblendedCost']['Amount']
                unit = group['Metrics']['UnblendedCost']['Unit']
                print(result_by_time['TimePeriod']['Start'], '\t', '\t'.join(group['Keys']), '\t', amount, '\t', unit, '\t', result_by_time['Estimated'])

if __name__ == "__main__":
    app = GetCostPerUser()
    app.create_session_for_cost_explorer()
    res = app.get_result()
    app.generate_csv(res)
