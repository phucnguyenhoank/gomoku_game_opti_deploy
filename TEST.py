BOARD_SIZE = 6

for di in range(BOARD_SIZE-1, -BOARD_SIZE, -1):
    a = []
    # print(f"a={di}b={di + BOARD_SIZE}")
    # ràng buộc range(max(0, di), min(BOARD_SIZE, di + BOARD_SIZE)) được dùng để đảm bảo rằng
    # với mọi giá trị của di thì i luôn chạy trong các đoạn con thuộc đoạn [0, BOARD_SIZE]
    # cụ thể
    # min(BOARD_SIZE, di + BOARD_SIZE) nói rằng nếu như bằng cách nào đó di + BOARD_SIZE bị vượt quá thì nó sẽ bị cắt xuống thành BOARDSIZE cho hợ lệ
    # max(0, di) nói rằng nếu như bằng cách nào đó di bé hơn không thì nó sẽ được nâng lên thành 0 cho hợ lệ
    # kết hợ ràng buộc đó với giá trị của di để buộc biến i được duyệt chạy trong đoạn 4, 3, 2, 1, 0, 0, 0, 0, 0 (Đối với N = 5)
    for i in range(max(0, di), min(BOARD_SIZE, di + BOARD_SIZE)):
        #print(i, end=" ")
        a.append((i, i - di))
    #print()
    print(a)

print("---")

for di in range(BOARD_SIZE-1, -BOARD_SIZE, -1):
    a = []
    for i in range(max(0, di), min(BOARD_SIZE, di + BOARD_SIZE)):
        a.append((i, BOARD_SIZE - 1 - (i - di)))
    print(a)
