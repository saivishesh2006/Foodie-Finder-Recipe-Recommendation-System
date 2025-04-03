import pandas as pd

df=pd.read_csv('final_Indian_Dataset.csv')

print(df['TotalTimeInMins'].max(),df['TotalTimeInMins'].min())






