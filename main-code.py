import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy.signal import find_peaks

script_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(script_dir, "daily_sunspots.csv") #there were some issues with finding the right file in VS Code space, so this alternative route was chosen for it 
df = pd.read_csv(csv_path)
df["date"] = pd.to_datetime(df["date"])
df["counts"] = df["counts"].replace(-1, np.nan) #replacing missing data set with not a number

#montly averages
monthly_df = (df.groupby(pd.Grouper(key="date", freq = "ME")) ["counts"].mean().reset_index())

#moving average in a span of 13 month window
monthly_df["moving_average"] = (monthly_df["counts"].rolling(window=13, center = True, min_periods=1)).mean() #min_periods allow averages neat adges and avoids NaNs, 13-month window is used to flatten out annual bumps so the curve will be smooth

signal = monthly_df["moving_average"].to_numpy() #converting pandas series into numpy array
peaks, properties = find_peaks(signal, distance=90, prominence=15) #setting distance to choose the highest one if there is any bumps and proinence says how much the peak stands out from baseline
peak_df = monthly_df.iloc[peaks] #exact dates where peaks occured, locates integers fo selection

#adding peak dates in a form of a list, will be used for prediction as well
peak_dates = monthly_df["date"].iloc[peaks].tolist() #iloc positions integers, tolist()converts a panda series into a list
peak_values = monthly_df["moving_average"].iloc[peaks]
cycle_duration = [(peak_dates[N] - peak_dates[N - 1]).days / 365.25 for N in range(1, len(peak_dates))]#dt.days = returns day value, number of years between the consecutive dates of peaks

avg_cycle = np.mean(cycle_duration)
std_cycle = np.std(cycle_duration)
avg_peak_height = np.mean(peak_values)
std_peak_height = np.std(peak_values)
maximum_peak_value = np.max(peak_values) #using built-in function so both minimum and maximu can be displayed for better visulaization of data
minimum_peal_value = np.min(peak_values)

plt.figure(figsize=(10, 5))

#montly period - moving average
plt.plot(monthly_df["date"], monthly_df["moving_average"], color="tab:brown", label = "13-month average")
plt.scatter(monthly_df["date"].iloc[peaks], monthly_df["moving_average"].iloc[peaks], label="Solar Peaks")
#adding a horizontal line spanning an axes
plt.axhline(y=avg_peak_height, color="grey", linestyle="--", label=f"Mean of a peak ({avg_peak_height: .2f})")

plt.title("Historical Solar Cycle Peaks")
plt.xlabel("Dates")
plt.ylabel("Sunspots")
plt.xlim(monthly_df["date"].min(), monthly_df["date"].max())
plt.ylim(bottom=0, top=maximum_peak_value * 1.4) #the max is multiplied by 1.4 so there is enough space 
plt.legend(loc="upper right", frameon = True) #setting location of the legend in the upper right corner, frameon will put the legend into a box = it is just for better visualization
plt.tight_layout() #adjusts the setting so nothing overlaps or gets cut off

plt.savefig("sunspot tracking.png")

print(f"{len(peak_dates)} peaks were detected.")
print(f"Average Length of Solar cycle {avg_cycle} ± {std_cycle}")
print(f"Average Amplitude of a Peak: {avg_peak_height} ± {std_peak_height}")

#making predictions
last_peak = peak_dates[-1] #selects the final row
number_future_cycles = 3
future_peaks = []
average_peak_height = np.mean(peak_values)

plt.figure(figsize=(12,6))

for i in range(1, number_future_cycles + 1):
    prediction_days = avg_cycle * i * 365.25 #converting to days
    std_predicted_days = std_cycle * np.sqrt(i) * 365.25

    predicted_date = last_peak + pd.Timedelta(days=prediction_days) #timedelta shows amount of time not specififc date
    lower_bound = last_peak + pd.Timedelta(days=prediction_days - std_predicted_days)
    upper_bound = last_peak + pd.Timedelta(days=prediction_days + std_predicted_days)

    if i == 1:
        x_offset, y_offset = -15, 18
    elif i == 2:
        x_offset, y_offset = 0, 55
    else: 
        x_offset, y_offset = 15, 18    
    
    plt.annotate(f"Cycle +{i}, {predicted_date.strftime('%Y-%m')}", xy=(predicted_date, average_peak_height), xytext=(x_offset, y_offset), ha="center", color="crimson", textcoords="offset points", bbox=dict(boxstyle="round,pad=0.3", facecolor="white")) #ha = makes sure that the text string is alligned horizontally in the middle, bbox is a new function i just found and it puts data nicely into a box for cleas depiction

    future_peaks.append((predicted_date, lower_bound, upper_bound))
    print(f"Cycle number: {i}   Predicted peak: {predicted_date.strftime('%Y-%m')}")

plt.plot(monthly_df["date"], monthly_df["moving_average"], color="brown", label="13-months moving average")
plt.scatter(peak_dates, peak_values, color="black", label="Historicl Peaks")

plt.title("Predicting future sunspot tracking", fontweight="bold")
plt.xlabel("Date")
plt.ylabel("Sunspots")
plt.xlim(left=pd.Timestamp("1850-01-01"), right=future_peaks[-1][0] + pd.Timedelta(days=5 * 365.25)) #setting limits so all the predicted days will be dispalyed and shown, adding extra 5 years so there is some extra space
plt.ylim(bottom=0, top=max(peak_values) * 1.4) #sets the limits, the max is multiplied by 1.4 so the text and graoh do not collide and there is some space for the information
plt.legend(loc="upper left", frameon=True) #loc controls where the legend appears, frameon puts the legenfd into the frame = its just to make it more clear and understandable
plt.grid(True, alpha=0.3)
plt.tight_layout() #adjusts the setting so nothing overlaps or gets cut off

plt.savefig("sunspot_predictions.png")
plt.show()
