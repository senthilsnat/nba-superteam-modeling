import numpy as np
import operator
from sklearn.decomposition import PCA
from sklearn import preprocessing
import matplotlib
matplotlib.use('TkAgg')
from matplotlib import pyplot as plt
from radar import radar_graph

# import and look at training data
with open("WarriorsLineupComps.csv", 'r') as myFile:
    dataLines = myFile.readlines()

data_temp = []
for z in range(1, len(dataLines)):
    data_temp.append(dataLines[z].split(','))
    # print data_temp[x-1]

data = []
for i in range(len(data_temp)):
    temp = []
    for j in range(1, len(data_temp[0])-1):
        if data_temp[i][j] == '':
            temp.append(0)
        else:
            temp.append(float(data_temp[i][j]))
    temp.append(str(data_temp[i][0]))
    temp.append(float(data_temp[i][-1]))

    data.append(temp)


# scale data
train = data
temp = np.array(data)
scaler = preprocessing.StandardScaler().fit(temp[:, 0:-2])
trainer = scaler.transform(temp[:, 0:-2]).tolist()

# print train[0]

# import and look at testing data
with open("WarriorsLineup.csv", 'r') as myFile:
    dataLines = myFile.readlines()

data_temp = []
for z in range(1, len(dataLines)):
    data_temp.append(dataLines[z].split(','))
    # print data_temp[x-1]

data = []
for i in range(len(data_temp)):
    temp = []
    for j in range(1, len(data_temp[0])):
        if data_temp[i][j] == '':
            temp.append(0)
        else:
            temp.append(float(data_temp[i][j]))
    temp.append(str(data_temp[i][0]))

    data.append(temp)

# scale data
test = data
temp = np.array(data)
tester = scaler.transform(temp[:, 0:-1]).tolist()


# find two norm distance
def twonorm(point1, point2, length):
    dist = 0
    for n in range(length):
        # death lineup is built on: shooting, excellent individual defenders, and great passers at unconventional spots
        # prioritize ball movement, scoring efficiency and defense, so weight AST/PTS/3P% and STL/BLK/DBPM error
        # But don't reward STL/BLK as heavily since they're more imperfect markers of defense
        # allow the comps to be better - reward by decreasing weight if better, penalize by weighting up if worse

        # some standing reaches used are estimates

        # you don't want to just set the reward to zero distance because i.e. obviously
        # Lebron will be better than Beverley in most areas, but he's not a good comp for beverley

        if ((n == 5) or (n == 8) or (n == 10) or (n == 13)) and ((point1[n] - point2[n]) > 0):
            dist += (((point1[n] - point2[n])*3)**2)

        elif ((n == 5) or (n == 8) or (n == 10) or (n == 13)) and ((point1[n] - point2[n]) < 0):
            dist += (((point1[n] - point2[n])*0.33)**2)

        elif ((n == 6) or (n == 7)) and ((point1[n] - point2[n]) > 0):
            dist += (((point1[n] - point2[n])*2)**2)

        elif ((n == 6) or (n == 7)) and ((point1[n] - point2[n]) < 0):
            dist += (((point1[n] - point2[n])*0.5)**2)

        else:
            dist += ((point1[n] - point2[n])**2)


    return np.sqrt(dist)


# get array of distances for each test point
def find_distances(trainers, testers):
    distances = []
    length = len(testers)
    for x in range(len(trainers)):
        dist = twonorm(testers, trainers[x], length)
        # store as tuples of the actual training data and the distance
        distances.append((train[x], dist))
    # sort the tuples by distance
    distances.sort(key=operator.itemgetter(1))
    return distances


# run spider for visualizing radar charts for non-cost-controlled solutions
def spider(which_trainer, which_tester):

    # get distances to all neighbors for each testing point and put in a big array
    distances_arr = []
    for x in range(len(which_tester)):
            distances = find_distances(which_trainer, which_tester[x])
            distances_arr.append(distances)

    comps = []
    comps_raw = []
    # for each testing point...
    for x in range(len(which_tester)):

        # don't repeat comps
        if distances_arr[x][0][0][-2] not in comps_raw:
            test_comp1 = distances_arr[x][0][0][-2]
        else:
            test_comp1 = distances_arr[x][1][0][-2]

        # test_comp2 = distances_arr[x][1][0][-2]
        # test_comp3 = distances_arr[x][2][0][-2]
        result = [test_comp1]
        comps_raw.append(test_comp1)
        comps.append([result, test[x][-1], distances_arr[x][0][1]])

        # prepare data for feeding into radar chart
        store = []
        lab_store = []
        for p in result:
            temp_store = []
            lab_store_temp = []
            for m in range(len(train)):
                if train[m][-2] == p:
                    train_temp = []
                    for l in range(len(trainer[m])):
                        train_temp.append(trainer[m][l] + 6)
                    # print train[m][-1], train_temp
                    lab_store_temp.append(train[m][-2])
                    temp_store.append([train_temp, train[m][-2]])

            store.append(temp_store[0])
            lab_store.append(lab_store_temp[0])

        for p in range(len(tester[x])):
            tester[x][p] += 6  # Drummond sucks so much I need to raise by 6 to take his FT% positive for viz purposes

        # create radar chart with parameters: name of base player, axes labels, legend labels, 4 data sets
        # base player chart will be filled in and 3 comps will just be edge maps
        # ...visually speaking, how well can we color within the lines?
        label = dataLines[0].split(',')
        label.remove('Player')
        case = tester[x]
        print case
        comp1 = store[0][0]
        name = test[x][-1]
        leg_lab = (test[x][-1], lab_store[0])
        radar_graph(name, label, leg_lab, case, comp1)

    cost = 0
    print "In format: [['comp'], 'original player', error]"
    for m in comps:
        print m
        for n in train:
            if n[-2] == m[0][0]:
                cost += n[-1]

    print "cost =", cost


# run spider_reg for final cost-controlled solutions
def spider_reg(which_trainer, which_tester):
    # get distances to all neighbors for each testing point and put in a big array
    distances_arr = []
    for x in range(len(which_tester)):
            distances = find_distances(which_trainer, which_tester[x])
            distances_arr.append(distances)

    comps = []
    comps_raw = []
    # for each testing point...
    for x in range(len(which_tester)):
        print test[x][-2]
        # don't repeat comps
        for y in distances_arr[x]:

            # as long as the player is not already being used
            # and as long as the standing reach is within 3 inches of the test player if not longer...
            if (y[0][-2] not in comps_raw) and ((y[0][-3] - test[x][-2]) >= -3):
                test_comp1 = y[0][-2]
                break

        result = [test_comp1]
        comps_raw.append(test_comp1)
        comps.append([result, test[x][-1], distances_arr[x][0][1]])

    cost = 0
    for m in comps:
        for n in train:
            if n[-2] == m[0][0]:
                cost += n[-1]
                m.append(n[-1])

    print comps
    print "original cost =", cost
    print comps_raw

    print distances_arr[1]

    if cost <= 15:
        print "we're fine!"
        return comps

    # run a descent-based minimization function to find optimal lineup that is under cost limits
    # minimize cost, optimize comp lineup with least "error"/distance from original lineup
    while cost > 15:
        new_comps = []
        new_comps_raw = []

        for m in comps:
            # print m
            ind = comps.index(m)
            if m[-1] != 1.0:
                for y in distances_arr[ind]:

                    if (y[0][-2] not in comps_raw) and (y[0][-1] < m[-1]):
                        # print "maybe?"
                        new_comps.append([[y[0][-2]], test[ind][-1], y[1], y[0][-1]])
                        new_comps_raw.append(y[0][-2])
                        break

        # print distances_arr[0]
        # print "unsorted version"
        # print new_comps

        new_comps = sorted(new_comps, key=lambda player: player[-2])

        # print "sorted version"
        # print new_comps

        for old in comps:
            if old[1] == new_comps[0][1]:
                ind = comps.index(old)
                comps[ind] = new_comps[0]
                comps_raw[ind] = new_comps[0][0][0]

        print "old cost =", cost
        cost = 0
        for m in comps:
            for n in train:
                if n[-2] == m[0][0]:
                    cost += n[-1]

        print "new cost =", cost
        # print comps
        print "new lineup =", comps_raw
        print comps

    # prepare data for feeding into radar chart
    store = []
    lab_store = []
    for p in comps_raw:
        temp_store = []
        lab_store_temp = []
        for m in range(len(train)):
            if train[m][-2] == p:
                train_temp = []
                for l in range(len(trainer[m])):
                    train_temp.append(trainer[m][l] + 6)
                # print train[m][-1], train_temp
                lab_store_temp.append(train[m][-2])
                temp_store.append([train_temp, train[m][-2]])

        store.append(temp_store[0])
        lab_store.append(lab_store_temp[0])

    # sometimes people have absurdly low stats so just raise all by 6 for viz purposes
    for p in tester:
        for x in range(len(p)):
            p[x] += 6

    # create radar chart with parameters: name of base player, axes labels, legend labels, 4 data sets
    # base player chart will be filled in and 3 comps will just be edge maps
    # ...visually speaking, how well can we color within the lines
    for n in store:
        ind = store.index(n)
        label = dataLines[0].split(',')
        label.remove('Player')
        case = tester[ind]
        # print case
        comp1 = store[ind][0]
        name = test[ind][-1]
        leg_lab = (test[ind][-1], lab_store[ind])
        radar_graph(name, label, leg_lab, case, comp1)


# interesting note...once you get to the 1s, you have to basically make a hard trade-off between DBPM and 3P%
# Reddick is 47% from 3, only plausible swap options: Korver, Marvin, Batum...Bobcats have some good bargain bin wings

# run final solution
spider_reg(trainer, tester)

