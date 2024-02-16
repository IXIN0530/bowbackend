def get_day(array):
    day_data=array[1:]
    separated=[]
    separated.append(["年",day_data.split("年")[0]])
    separated.append(["月",day_data.split("年")[1].split("月")[0]])
    separated.append(["日",day_data.split("年")[1].split("月")[1].split("日")[0]])
    return separated