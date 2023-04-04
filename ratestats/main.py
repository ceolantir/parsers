from extractions import RateStatsData


if __name__ == "__main__":
    days_delta = 2
    data = RateStatsData(days_delta).start()
    print(data)
