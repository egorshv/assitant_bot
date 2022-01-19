import matplotlib.pyplot as plt


def create_plot(dates, prices, filename, title):
    plt.ylabel('price')
    plt.xlabel('date')
    plt.figure(figsize=(len(dates) + 2, len(prices)))
    plt.title(title)
    plt.plot(dates, prices)
    plt.savefig(filename)

# dates = ['13.12.2021', '07.01.2022', '24.02.2022', '30.03.2022', '14.04.2022', '08.05.2022', '17.06.2022']
# prices = [28500, 27000, 26500, 28000, 29500, 29000, 27000]
# create_plot(dates, prices, 'test.png')
