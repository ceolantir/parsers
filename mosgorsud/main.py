from extractions import MosGorSudData


if __name__ == "__main__":
    params = {
        'court': 'Московский городской суд',
        'instance': 'Первая',
        'process': 'Административное',
    }
    data = MosGorSudData(params).start()
    print(data)
