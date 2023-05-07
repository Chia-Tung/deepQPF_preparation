import os

def listdir(path: str, rev: bool = True) -> str:
    """
    return the latest dir/file in one level
    """
    return sorted(os.listdir(path), reverse=rev)[0]  # from large to small


def get_latest(dir: str) -> str:
    year = listdir(dir)
    yearMonth = listdir(os.path.join(dir, year))
    yearMonthDay = listdir(os.path.join(dir, year, yearMonth))
    file = listdir(os.path.join(dir, year, yearMonth, yearMonthDay))
    return os.path.join(dir, year, yearMonth, yearMonthDay, file)