import json
import sys
from datetime import datetime, timedelta

def get_dict_of_last_quarters(num_last_quarters):
    current_date = datetime.now()
    quarters = {}

    for i in range(num_last_quarters):
        quarter = (current_date.month - 1) // 3 + 1
        year = current_date.year
        quarters[f'Q{quarter} {year}'] = 0
        current_date -= timedelta(days=90)  # Approximate 3 months back

    return quarters

def get_quarter(date_str):
    # Parse the date string
    date = datetime.strptime(date_str, '%Y-%m-%d')

    # Determine the quarter
    quarter = (date.month - 1) // 3 + 1

    # Format the result as "QX YYYY"
    return f'Q{quarter} {date.year}'


def main():
    # Python Version 3.8 or higher is required for this script to work (order of dictionary items is guaranteed)
    # check if the python version is 3.8 or higher
    if sys.version_info < (3, 8):
        print('Python 3.8 or höher wird benötigt.')
        sys.exit(1)

    # Read JSON content from file
    with open('transaktionen.json', 'r') as file:
        json_input = file.read()

    # Parse JSON content
    data = json.loads(json_input)

    # Get the current bonus points from stdin or pass it as an argument
    if len(sys.argv) == 2:
        current_bonus_points = int(sys.argv[1])
    else:
        current_bonus_points = int(input('Bitte die aktuelle Anzahl der BahnBonus Punkte angeben: '))

    # a dictionary to store the total points per quarter
    bonus_points_per_quarter = get_dict_of_last_quarters(13)

    for transaction in data['transactions']:
        # Continue if the transaction is not earmarked (a future transaction) or a points expiration
        if not transaction['earmarked'] and not transaction['transactionCategory'] == 'Punkteverfall' and not transaction['transactionCategory'] == 'Prämienbestellung':
            quarter_of_transaction = get_quarter(transaction['transactionDate'])
            # Check if the quarter is in the dictionary, sometimes DB has transactions from before the last 13 quarters
            if quarter_of_transaction in bonus_points_per_quarter:
                bonus_points_per_quarter[quarter_of_transaction] += transaction['pointsBB']


    # Summarize the points per quarter
    sum_of_points = 0
    print("\nPro Quartal gesammelte Punkte:")
    for quarter, points in bonus_points_per_quarter.items():
        sum_of_points += points
        print(f'{quarter}: {points}')

    # print total points and current bonus points
    print(f'\nSumme der aus den Transaktionen berechneten Punkte: {sum_of_points}') # Sum of all points
    print(f'Aktuelle Anzahl der BahnBonus Punkte: {current_bonus_points}') # Current bonus points

    difference_in_points = sum_of_points - current_bonus_points

    if difference_in_points > 0:
        print(f'\nEs gibt einen Unterschied von {difference_in_points} Punkten. Dies stammt vrsl. von Prämienausgaben. Dies wird nun berücksichtigt.')
        for quarter, points in reversed(bonus_points_per_quarter.items()):
            if points < difference_in_points:
                bonus_points_per_quarter[quarter] = 0
                difference_in_points -= points
            else:
                bonus_points_per_quarter[quarter] -= difference_in_points
                break

    # print the final result
    print("\nIn Folgenden Quartalen laufen die Punkte ab:")

    # Print the final points per quarter + 3 years
    for quarter, points in reversed(bonus_points_per_quarter.items()):
        # increase the quarter by 3 years
        quarter = quarter.split()
        quarter[1] = str(int(quarter[1]) + 3)
        quarter = ' '.join(quarter)
        print(f'{quarter}: {points}')


if __name__ == '__main__':
    main()