import numpy as np


def top_k(a, k):
    ravel = a.ravel()
    idx = np.argpartition(ravel, a.size - k)[-k:]
    idx2 = np.argsort(-ravel[idx])
    return np.unravel_index(idx[idx2], a.shape)


if __name__ == "__main__":
    # a = np.array([[38, 14, 81, 50],
    #               [17, 65, 60, 24],
    #               [64, 73, 25, 95]])
    # print(a)
    # row, col = top_k(a, 2)
    # print(row, col)

    import time
    from sklearn.metrics.pairwise import cosine_similarity

    x = np.random.rand(10, 128)
    y = np.random.rand(1000000, 128)
    z = cosine_similarity(x, y)
    start_time = time.time()
    top = top_k(z, 3)
    print(top)
    print(time.time() - start_time)
