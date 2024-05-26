from datetime import datetime
import pandas as pd
import os

def update_csv():
    directory = 'data'
    filename = os.path.join(directory, 'runs.csv')
    
    # create directory if it doesnt exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    df = pd.DataFrame([{'cronjob_run': datetime.now()}])
    
    if not os.path.isfile(filename):
        df.to_csv(filename, index=False)

    else:
        df.to_csv(filename, mode='a', header=False, index=False)

if __name__ == "__main__":
    update_csv()
