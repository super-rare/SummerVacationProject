# 20180805 programmed by Himchan Park, KyeongHee Univ. Dept. of Computer science

#include
import chess
import random
import time
import os
import copy

#depth meter, if too slow, pull down it
depth = 3
#time limit, if too slow, pull down it
time_limit = 60

#define function
def parse_uci(uci): # chess-movement
    uci = str(uci)
    a_to_n = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    xindex = 0
    yindex = int(uci[3]) - 1
    for i in range(8):
        if uci[2] == a_to_n[i]:
            xindex = i
            break
    pos = [yindex, xindex]
    return pos


def weight_calculate(target, weight_list): #calculates weight of that node
    if target == '.':
        return 0
    else:
        if target == 'p' or target == 'P':
            return float(weight_list[0])
        if target == 'n' or target == 'N':
            return float(weight_list[1])
        if target == 'b' or target == 'B':
            return float(weight_list[2])
        if target == 'r' or target == 'R':
            return float(weight_list[3])
        if target == 'q' or target == 'Q':
            return float(weight_list[4])
        if target == 'k' or target == 'K':
            return 9999

def who_is_target(pos): #finds attacks' target
    search_list = str(board)
    index = 8 * (8 - pos[0] - 1) + pos[1] + 1
    target = search_list[2 * (index - 1)]
    return target


def alpha_beta(depth, alpha, beta, ifmax, weight_list, limit): # ai
    legal_list = list(board.legal_moves)
    random.shuffle(legal_list)
    move = chess.Move.null()
    load_time = time.time()
    
    if board.is_variant_win(): # end of node
        if ifmax:
            return [9999, chess.Move.null()]
        else:
            return [9999, chess.Move.null()]

    if depth == 0:
        if ifmax:
            tmp = -99999
            for move in legal_list:
                pos = parse_uci(move)
                if weight_calculate(who_is_target(pos), weight_list) >= tmp:
                    tmp = weight_calculate(who_is_target(pos), weight_list)
            return [tmp, move]
        else:
            tmp = 99999
            for move in legal_list:
                pos = parse_uci(move)
                if - weight_calculate(who_is_target(pos), weight_list) <= tmp:
                    tmp = -weight_calculate(who_is_target(pos), weight_list)
            return [tmp, move]

    if ifmax:
        value = -99999
        for move in legal_list:
            pos = parse_uci(move)
            board.push(move)
            value = max(value, weight_calculate(who_is_target(pos), weight_list) + \
                        alpha_beta(depth - 1, alpha, beta, False, weight_list, limit)[0])
            alpha = max(alpha, value)
            board.pop()
            if beta < alpha or time.time() - load_time > limit: 
                break # beta cut-off
        return [value, move]
    else:
        value = 99999
        for move in legal_list:
            pos = parse_uci(move)
            board.push(move)
            value = min(value, (weight_calculate(who_is_target(pos), weight_list) - \
                        alpha_beta(depth - 1, alpha, beta, True, weight_list, limit)[0]))
            beta = max(beta, value)
            board.pop()
            if beta < alpha or time.time() - load_time > limit: 
                break # alpha cut-off
        return [value, move]

    
#main
f = open('weightlist.txt', 'r')
weight_list = list()
for line in f.readlines():
    weight_list.append(line.strip().split())
f.close()
num = int(weight_list[-1][0])
weight_list.pop()

while True:
    
    result = list()
    for i in range(len(weight_list)):
        result.append(0)
    print('generation', num)
    
    for i in range(len(weight_list)):
        for j in range(i + 1, len(weight_list)):
            k = 1
            board = chess.Board()
            while True:
                if not board.is_checkmate():
                    ab = alpha_beta(depth, -99999, 99999, True, weight_list[i], time_limit/2)
                    board.push(ab[1])
                    print('Turn', k, ': WHITE')
                    print(board)
                    print(ab[0])
                    print()
                else:
                    print("player", i + 1,  "won")
                    result[i] += 1
                    break
                if not board.is_checkmate():
                    ab = alpha_beta(depth, -99999, 99999, True, weight_list[j], time_limit/2)
                    board.push(ab[1])
                    print('Turn', k, ': BLACK')
                    print(board)
                    print(ab[0])
                    print()
                else:
                    print("player", j + 1, "won")
                    result[j] += 1
                    break
                k = k + 1
                if board.is_variant_draw() or k >= 100:
                    print('draw.')
                    break
    print('result')
    for i in range(len(result)):
        print('Com', i, ':', result[i])
                    
    #cross
    cross = random.randint(0,4)
    fir = 0
    sec = 0
    last = 0
    least = 0
    for i in range(len(result)):
        if result[i] == max(result):
            fir = i
            result[i] = 0
            break
    for i in range(len(result)):
        if result[i] == max(result):
            sec = i
            break
    result[fir] = 15
    for i in range(len(result)):
        if result[i] == min(result):
            last = i
            result[i] = 15
            break
    for i in range(len(result)):
        if result[i] == min(result):
            least = i
            break

    weight_list[last] = copy.deepcopy(weight_list[fir])
    weight_list[least] = copy.deepcopy(weight_list[sec])
    
    if cross != 4:
        print('Cross : Y')
        for i in range(cross, 4):
            tmp = weight_list[last][i + 1]
            weight_list[last][i + 1] = weight_list[least][i + 1]
            weight_list[least][i + 1] = tmp
    else:
        print('Cross : N')
        
    #mutate
    whether_mutate = bool(random.randint(0,1))
    mut_pos = random.randint(0,4)
    mut_num = random.randint(0,len(weight_list) - 1)
    if whether_mutate:
        weight_list[mut_num][mut_pos] = random.randint(1, 9999)
        print('Mutate : Y')
    else:
        print('Mutate : N')

    #write
    f = open('weightlist.txt', 'w')
    for i in range(len(weight_list)):
        print('Com', i + 1, ':', weight_list[i])
        for j in weight_list[i]:
            f.write(str(j))
            f.write(' ')
        f.write('\n')
    num += 1
    f.write(str(num))
    f.close()

    #next gen?
    while True:
        next = input('Move to next generation?(y/n) : ')
        if next == 'y' or next == 'n':
            break
    if next == 'n':
        break
os.system('pause')
