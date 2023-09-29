import datetime
from sql_helper import SqlHelper # TODO : Replace the module and the class name of the sql lambda layer

# Initialize SQL helper
sql_helper = SqlHelper()

def lambda_handler(event, context):
    # Get mail_id from event
    mail_id = event['mail_id']

    if not mail_id:
        return {
            'statusCode': 400,
            'body': dict(error='Mail id is required')
        }

    data = sql_helper.get_chats(mail_id)

    meta_data = dict(
                    today = [],
                    yesterday = [],
                    this_week = [],
                    current_month = [],
                    earlier_months = []
                )

    if data:
        data = data.json
        # group the data by date
        groups = {}
        for item in data:
            date = datetime.datetime.strptime(item["created_at"], "%Y-%m-%d %H:%M:%S").date()
            if date not in groups:
                groups[date] = []
            groups[date].append(item)

        # categorize the groups by date range
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        last_week = today - datetime.timedelta(days=7)
        last_month = today - datetime.timedelta(days=30)

        today_data = []
        yesterday_data = []
        last_week_data = []
        last_month_data = []
        earlier_data = []

        for date, items in groups.items():
            if date == today:
                today_data.extend(items)
            elif date == yesterday:
                yesterday_data.extend(items)
            elif date >= last_week and date < today:
                last_week_data.extend(items)
            elif date >= last_month and date < last_week:
                last_month_data.extend(items)
            else:
                earlier_data.extend(items)

        meta_data['today'] = today_data[::-1]
        meta_data['yesterday'] = yesterday_data[::-1]
        meta_data['this_week'] = last_week_data[::-1]
        meta_data['current_month'] = last_month_data[::-1]
        meta_data['earlier_months'] = earlier_data[::-1]

    # Return data to user
    return {
    'statusCode': 200,
    'body': meta_data
    }