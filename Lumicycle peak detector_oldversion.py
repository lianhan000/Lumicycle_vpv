import pandas as pd
import tkinter as tk
from tkinter import filedialog
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import os
import platform
import subprocess

root = tk.Tk()
root.withdraw()


def stop_program():
    plt.close()
    root.destroy()
    print('\nExit')


def save_to_excel(dataframe):
    file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])

    if file_path:
        result_combined = dataframe.copy()
        final_df = pd.concat([dataframe, result_combined])

        final_df.drop_duplicates(keep='first', inplace=True)

        with pd.ExcelWriter(file_path) as writer:
            final_df.to_excel(writer, index=False)
        print('\nData saved')

        if platform.system() == 'Windows':
            os.startfile(file_path)
        else:
            subprocess.Popen(['xdg-open', file_path])


def run_analysis():
    pathway = filedialog.askopenfilename()
    print('\nFile pathway:', pathway)
    file_name = os.path.splitext(os.path.basename(pathway))[0]

    df = pd.read_csv(pathway, header=1)
    # df.set_index('Unnamed: 0', inplace=True)
    df_count = df['counts/sec'].values
    df_count_minus = df['counts/sec'].values * (-1)

    peak_indices, _ = find_peaks(df_count)
    peaks = df.iloc[peak_indices].copy()

    trough_indices, _ = find_peaks(df_count_minus)
    troughs = df.iloc[trough_indices].copy()

    time = 'Time (days)'
    if time in df.columns:
        peak_time = df.loc[peak_indices, time]
        trough_time = df.loc[trough_indices, time]  # 替换变量名为trough_time
    else:
        print(f"Warning: Column '{time}' does not exist")
        peak_time, trough_time = None, None

    start_time = df.loc[0, time]
    print('\nStart time: ', start_time)

    peaks.loc[:, 'Time (Hours)'] = (peaks[time] - start_time) * 24
    troughs.loc[:, 'Time (Hours)'] = (troughs[time] - start_time) * 24

    result_df = pd.DataFrame({
        'Type': ['Peak'] * len(peaks) + ['Trough'] * len(troughs),  # 类型
        'No.': list(range(1, len(peaks) + 1)) + list(range(1, len(troughs) + 1)),  # 编号，峰值从0开始，谷值从1开始
        'counts/sec': pd.concat([peaks['counts/sec'], troughs['counts/sec']]),
        'Time (Day)': pd.concat([peak_time, trough_time]),
        'Time (Hours)': pd.concat([peaks['Time (Hours)'], troughs['Time (Hours)']])
    })

    print('\n', result_df)


    plt.ion()
    plt.figure(figsize=(6, 4))
    plt.plot(df['Time (days)'], df['counts/sec'], color='black')
    plt.scatter(peaks[time], peaks['counts/sec'], color='blue', label='Peak')
    plt.scatter(troughs[time], troughs['counts/sec'], color='red', label='Trough')

    for index, (x, y) in enumerate(zip(peaks[time], peaks['counts/sec'])):
        plt.text(x, y + 3, str(index + 1), ha='center', va='bottom', color='blue')
    for index, (x, y) in enumerate(zip(troughs[time], troughs['counts/sec'])):
        plt.text(x, y - 3, str(index + 1), ha='center', va='top', color='red')
    plt.xlabel('Time (days)')
    plt.ylabel('counts/sec')
    plt.legend()
    plt.title(file_name)
    plt.show()


    plot_path = os.path.join(os.path.dirname(pathway), f"plot_{file_name}.png")
    plt.savefig(plot_path)
    print('\nPlot saved')

    save_to_excel(result_df)

    plt.ioff()
    plt.clf()


window = tk.Toplevel(root)
window.title("Lumicycle Analysis")
window.geometry("200x150")

start_button = tk.Button(window, text="Open file", command=run_analysis)
start_button.pack(pady=20)

stop_button = tk.Button(window, text="Exit", command=stop_program)
stop_button.pack(pady=10)

root.mainloop()
