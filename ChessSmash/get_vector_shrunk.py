import math
def get_vector_shrunk(point1, point2, shrinkTo):
    distanceX = point1[0] - point2[0]
    distanceY = point1[1] - point2[1]
    vector = [distanceX, distanceY]
    hypotenuse = math.sqrt((distanceX**2) + distanceY**2)
    shrinkFactor = shrinkTo/hypotenuse
    vector = [vector[0]*shrinkFactor, vector[1]*shrinkFactor]
    return vector
print(get_vector_shrunk([0,0], [2,2], 1))