from dumpy.matrix import Matrix, Point3D, Vector3D, identity


def test_matrix():
    # equality
    m1 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    m2 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    assert m1 == m2
    m1 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    m2 = Matrix([[2, 3, 4, 5], [6, 7, 8, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    assert m1 != m2
    # element-wise arithmetic
    assert Point3D(3, -2, 5) + Vector3D(-2, 3, 1) == Point3D(1, 1, 6)
    assert Point3D(3, 2, 1) - Point3D(5, 6, 7) == Vector3D(-2, -4, -6)
    assert Point3D(3, 2, 1) - Vector3D(5, 6, 7) == Point3D(-2, -4, -6)
    assert Vector3D(3, 2, 1) - Vector3D(5, 6, 7) == Vector3D(-2, -4, -6)
    assert Matrix([[1, -2, 3, -4]]) * 3.5 == Matrix([[3.5, -7, 10.5, -14]])
    assert 0.5 * Matrix([[1, -2, 3, -4]]) == Matrix([[0.5, -1, 1.5, -2]])
    assert Matrix([[1, -2, 3, -4]]) / 2 == Matrix([[0.5, -1, 1.5, -2]])
    # magnitude and normalization
    assert Vector3D(1, 0, 0).magnitude == 1
    assert Vector3D(0, 1, 0).magnitude == 1
    assert Vector3D(0, 0, 1).magnitude == 1
    assert Vector3D(2, 3, 6).magnitude == 7
    assert Vector3D(-2, -3, -6).magnitude == 7
    assert Vector3D(4, 0, 0).normalize() == Vector3D(1, 0, 0)
    assert Vector3D(1, 2, 3).normalize().magnitude == 1
    # dot and cross product
    assert Vector3D(1, 2, 3).dot(Vector3D(2, 3, 4)) == 20
    assert Vector3D(1, 2, 3).cross(Vector3D(2, 3, 4)) == Vector3D(-1, 2, -1)
    assert Vector3D(2, 3, 4).cross(Vector3D(1, 2, 3)) == Vector3D(1, -2, 1)
    # matrix multiplication
    m1 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    m2 = Matrix([[-2, 1, 2, 3], [3, 2, 1, -1], [4, 3, 6, 5], [1, 2, 7, 8]])
    m3 = Matrix([[20, 22, 50, 48], [44, 54, 114, 108], [40, 58, 110, 102], [16, 26, 46, 42]])
    assert m1 @ m2 == m3
    m1 = Matrix([[1, 2, 3, 4], [2, 4, 4, 2], [8, 6, 4, 1], [0, 0, 0, 1]])
    assert m1 @ Point3D(1, 2, 3) == Point3D(18, 24, 33)
    m1 = Matrix([[0, 1, 2, 4], [1, 2, 4, 8], [2, 4, 8, 16], [4, 8, 16, 32]])
    m2 = identity(4)
    assert m1 @ m2 == m1
    # transposition
    m1 = Matrix([[0, 9, 3, 0], [9, 8, 0, 8], [1, 8, 5, 3], [0, 0, 5, 8]])
    m2 = Matrix([[0, 9, 1, 0], [9, 8, 8, 0], [3, 0, 5, 5], [0, 8, 3, 8]])
    assert m1.transpose() == m2
    assert m1.transpose().transpose() == m1
    assert identity(4).transpose() == identity(4)
    # determinant
    assert Matrix([[1, 5], [-3, 2]]).determinant == 17
    assert Matrix([[1, 5, 0], [-3, 2, 7], [0, 6, -3]]).submatrix(0, 2) == Matrix([[-3, 2], [0, 6]])
    assert Matrix([[-6, 1, 1, 6], [-8, 5, 8, 6], [-1, 0, 8, 2], [-7, 1, -1, 1]]).submatrix(2, 1) == Matrix([[-6, 1, 6], [-8, 8, 6], [-7, -1, 1]])
    assert Matrix([[3, 5, 0], [2, -1, -7], [6, -1, 5]]).minor(1, 0) == 25
    m = Matrix([[3, 5, 0], [2, -1, -7], [6, -1, 5]])
    m.cofactor(0, 0) == -12
    assert m.cofactor(1, 0) == -25
    assert Matrix([[1, 2, 6], [-5, 8, -4], [2, 6, 4]]).determinant == -196
    assert Matrix([[-2, -8, 3, 5], [-3, 1, 7, 3], [1, 2, -9, 6], [-6, 7, 7, -9]]).determinant == -4071
    # inverse
    m1 = Matrix([[3, -9, 7, 3], [3, -8, 2, -9], [-4, 4, 4, 1], [-6, 5, -1, 1]])
    m2 = Matrix([[8, 2, 2, 2], [3, -1, 7, 0], [7, 0, 5, 4], [6, -2, 0, 5]])
    assert m1 @ m2 @ m2.inverse() == m1
    # translation and scaling
    assert identity(4).translate(5, -3, 2) @ Point3D(-3, 4, 5) == Point3D(2, 1, 7)
    assert identity(4).translate(5, -3, 2).inverse() @ Point3D(-3, 4, 5) == Point3D(-8, 7, 3)
    assert identity(4).translate(5, -3, 2) @ Vector3D(-3, 4, 5) == Vector3D(-3, 4, 5)
    assert identity(4).scale(2, 3, 4) @ Point3D(-4, 6, 8) == Point3D(-8, 18, 32)
    assert identity(4).scale(2, 3, 4) @ Vector3D(-4, 6, 8) == Vector3D(-8, 18, 32)
    assert identity(4).scale(2, 3, 4).inverse() @ Point3D(-4, 6, 8) == Point3D(-2, 2, 2)
    # shear
    assert identity(4).shear(1, 0, 0, 0, 0, 0) @ Point3D(2, 3, 4) == Point3D(5, 3, 4)
    assert identity(4).shear(0, 1, 0, 0, 0, 0) @ Point3D(2, 3, 4) == Point3D(6, 3, 4)
    assert identity(4).shear(0, 0, 1, 0, 0, 0) @ Point3D(2, 3, 4) == Point3D(2, 5, 4)
    assert identity(4).shear(0, 0, 0, 1, 0, 0) @ Point3D(2, 3, 4) == Point3D(2, 7, 4)
    assert identity(4).shear(0, 0, 0, 0, 1, 0) @ Point3D(2, 3, 4) == Point3D(2, 3, 6)
    assert identity(4).shear(0, 0, 0, 0, 0, 1) @ Point3D(2, 3, 4) == Point3D(2, 3, 7)
