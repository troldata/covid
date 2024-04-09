
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sb
import os


def load_df_from_file (path_to_file):
    if not os.path.exists(path_to_file):
        print('File cannot be opened: ', path_to_file )
        exit()
        
    fhand = pd.read_csv(path_to_file, delimiter=',')
    return fhand   

# Statistik of hospital and beds in Germany

beds = load_df_from_file('Path to BedsGermany.csv')    

# drop: Delete columns
beds_drop = beds.drop(columns = ['Betten je 100.000 Einwohner', 'Patienten je 100.000 Einwohner',
                                 'Berechnungs-/Belegungstage -1000', 'Durchschnittliche Bettenauslastung-Prozent'])

#  Renaming
beds = beds_drop.rename(columns = {' Jahr':'year', 'Krankenhäuser': 'hospital', 'Betten': 'bed', 'Patienten':'patient', 'Durchschnittliche Verweildauer -Tage':'avarege_days'})

# Calculate reduction of hospitals and beds in Germany
value_hospital2010 = beds['hospital'].iloc[0]
value_bed2010 = beds['bed'].iloc[0]
beds = beds.assign(dif_hospital = lambda x: 
                   round((beds['hospital'])/value_hospital2010 * 100 -100, 2),
                   dif_bed = lambda x: round((beds['bed'])/value_bed2010 * 100 - 100, 2)) 
print('The new dataframe with changes in  beds and hospitals relative to 2010:')  
print(beds)
print()

# Covid file

df = load_df_from_file('Path to Covid_de.csv')
df.info() # we see, that date has object as Dtype
print()

df.date= pd.to_datetime(df.date)

df = df.sort_values(by=["date"], ascending=True)
df = df.dropna() # Delete NA row
df = df.reset_index(drop=True)

# Delete rows for 2022
mask = (df['date']<=pd.to_datetime('2022-02-28'))&(df['date'] >= pd.to_datetime('2020-03-01'))
df_new = df[mask]

print('The covid data from 2020-03-01 to 2022-02-28:')
print(df_new)
print()
 
# Cases und deaths in Germany

df_sums = df_new.groupby(['date']).sum()

plt.figure(figsize=(12,6))
first_day = pd.to_datetime('2020-03-01')
last_day = pd.to_datetime('2022-02-28')

datelist = pd.date_range(start = first_day, end = last_day).tolist()


# create two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot for cases
ax1.plot(datelist, df_sums.cases)
ax1.set_title('Confirmed cases')

plt.gcf().autofmt_xdate()

# Plot for deaths
ax2.plot(datelist, df_sums.deaths, color='r')
ax2.set_title('Deaths')

plt.gcf().autofmt_xdate()
for ax in [ax1, ax2]:
    ax.grid()
plt.show()



# Age of ill people_Piechart (country level)

df_age = df_new[['age_group','cases']].copy()
df_age = df_age.groupby(by = 'age_group').sum()
df_age['percent'] = round(100*(df_age['cases'] / sum(df_age['cases'])), 2)
df_age.sort_values('cases', ascending=False, inplace=True)
print('The covid cases in each age group:')
print(df_age)
print()

# Creating plot
fig = plt.figure(figsize = (8,6))
ax = fig.add_subplot()

vals = df_age['percent']
labels =df_age.index

ax.pie(vals, labels = labels, autopct ='%1.1f%%', shadow = True, textprops={'fontsize': 12} )

plt.title('Distribution of the cases in different age groups',fontsize=18)
plt.savefig('Distribution of the cases in different age groups.png')
plt.show()


# Age in death cases

df_age = df_new[['age_group','deaths']].copy()
df_age = df_age.groupby(by = 'age_group').sum()
df_age['percent'] = round(100*(df_age['deaths'] / sum(df_age['deaths'])), 2)
df_age.sort_values('deaths', ascending=False, inplace=True)
print('The death cases in each age group:')
print(df_age)
print()

sum_deaths = df_age.loc[df_age.index.isin(['80-99','60-79'])].sum()
print('Sum deaths in age group over 60 years old:') 
print(sum_deaths)
print()

# Cases by states

df_state = df_new[['state','cases']].copy()
covid_by_state = df_state.groupby('state').sum()
covid_by_state = covid_by_state.assign(cases_in_thousand = lambda x: round((covid_by_state['cases'])/ 1000, 1))
covid_by_state.sort_values('cases_in_thousand', ascending= False, inplace=True)
print('The covid cases by states:')
print(covid_by_state)
print()
sb.barplot(x=covid_by_state.cases_in_thousand, y=covid_by_state.index, palette="Spectral")
plt.title("Cases by states")
plt.show()


# Beds in states

bed_state = load_df_from_file('Path to BedsState.csv')
print('The beds in the each state:')
print(bed_state)
print()

bed_state = bed_state.iloc [1: , :]
bed_state.sort_values('bed', ascending= False, inplace=True)

state = bed_state['state'].tolist()  
bed = bed_state['bed'].tolist()  
sb.barplot(x=bed, y=state, palette="Spectral") 

plt.title('Beds in hospitals by states', fontsize=15)
plt.xlabel('state',fontsize=10)
plt.ylabel('bed',fontsize=10)



# Nordrhein-Westfalen

# Search value in dataframe 

df_state = df_new[['state','date','cases', 'deaths']].copy()
df_nw = df_state.loc[df_state['state'] == 'Nordrhein-Westfalen'].groupby('date').sum()

#create dictionary
dic_bed = bed_state[['state', 'bed']].set_index('state')['bed'].to_dict()
bed_nw=dic_bed['Nordrhein-Westfalen']

# insert bed in the table df_new
df_nw.insert(3, "bed_nw", bed_nw)
df_nw.head(5)

# Sliding data (cases)
def rolling(dataframe, window_size, column_name):
    rolling_sum = dataframe[column_name].rolling(window=window_size, min_periods=1).sum()
    return rolling_sum

wind_cases7 = rolling(df_nw, window_size=7, column_name='cases')
wind_cases14 = rolling(df_nw, window_size=14, column_name='cases')

# Plot

plt.figure(figsize=(12,6))
first_day = pd.to_datetime('2020-03-01')
last_day = pd.to_datetime('2022-02-28')
datelist = pd.date_range(start = first_day, end = last_day).tolist()

# create two subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

# Plot for cases - 7 days
ax1.plot(datelist, wind_cases7, label='confirmed cases', color='b')
ax1.plot(datelist, df_nw.bed_nw, label='bed', color='r')
ax1.set_title('Nordrhein-Westfalen, patiens are in hospital 7 days')
plt.gcf().autofmt_xdate()

# Plot for cases - 14 days
ax2.plot(datelist, wind_cases14, label='confirmed cases', color='b')
ax2.plot(datelist, df_nw.bed_nw, label='bed', color='r')
ax2.set_title('Nordrhein-Westfalen, patiens are in hospital 14 days')
plt.gcf().autofmt_xdate()

plt.legend()
for ax in [ax1, ax2]:
    ax.grid()
plt.show()






