import numpy as np

def get_sorted_top_k(array, top_k=1, axis=-1, reverse=False):
    """
    多维数组排序
    Args:
        array: 多维数组
        top_k: 取数
        axis: 轴维度
        reverse: 是否倒序

    Returns:
        top_sorted_scores: 值
        top_sorted_indexes: 位置
    """
    if reverse:
        # argpartition分区排序，在给定轴上找到最小的值对应的idx，partition同理找对应的值
        # kth表示在前的较小值的个数，带来的问题是排序后的结果两个分区间是仍然是无序的
        # kth绝对值越小，分区排序效果越明显
        axis_length = array.shape[axis]
        partition_index = np.take(np.argpartition(array, kth=-top_k, axis=axis),
                                  range(axis_length - top_k, axis_length), axis)
    else:
        partition_index = np.take(np.argpartition(array, kth=top_k, axis=axis), range(0, top_k), axis)
    top_scores = np.take_along_axis(array, partition_index, axis)
    # 分区后重新排序
    sorted_index = np.argsort(top_scores, axis=axis)
    if reverse:
        sorted_index = np.flip(sorted_index, axis=axis)
    top_sorted_scores = np.take_along_axis(top_scores, sorted_index, axis)
    top_sorted_indexes = np.take_along_axis(partition_index, sorted_index, axis)
    return top_sorted_scores, top_sorted_indexes


if __name__ == "__main__":
    import time
    from sklearn.metrics.pairwise import cosine_similarity

    x = np.random.rand(10, 128)
    y = np.random.rand(1000000, 128)
    z = cosine_similarity(x, y)
    start_time = time.time()
    sorted_index_1 = get_sorted_top_k(z, top_k=3, axis=1, reverse=True)[1]
    print(time.time() - start_time)
    start_time = time.time()
    sorted_index_2 = np.flip(np.argsort(z, axis=1)[:, -3:], axis=1)
    print(time.time() - start_time)
    print((sorted_index_1 == sorted_index_2).all())

