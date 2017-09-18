def search_data(data,target):
    # 中间值的索引号的定义：数组长度/2
    mid = len(data)//2
    # 判断从1开始的数字数组内查找
    if data[mid] >= 1:
        # 如果我们要找的值（target）比中间值（data[mid]）小
        if data[mid] > target:
            print("你要找的数字比中间值[%s]小..." % data[mid])
            # 在中间值（data[mid]）的左侧继续查找，在此函数中继续循环
            search_data(data[:mid],target)
        # 如果我们要找的值（target）比中间值（data[mid]）大
        elif data[mid] < target:
            print("你要找的数字比中间值[%s]大..." % data[mid])
            # 在中间值（data[mid]）的右侧继续查找，在此函数中继续循环
            search_data(data[mid:],target)
        else:
            # 如果我们要找的值（target）既不比中间值（data[mid]）大，也不比中间值（data[mid]）小，则就是它
            print("这就是你要找的[%s]！" % data[mid])
    else:
        print("不好意思，没有找到你要的值...")


def iterativeBinarySearch(data, target):
    first = 0
    last = len(data) - 1

    while first <= last:
        middle = (first + last) // 2
        if target == data[middle]:
            print(data[middle])
            return True
        elif target < data[middle]:
            last = middle - 1
        else:
            first = middle + 1
    return False


if __name__ == '__main__':

    data = list(range(60000000))
    search_data(data,95938)
    iterativeBinarySearch(data,95938)