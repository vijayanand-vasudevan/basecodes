// test

#include <iostream>
#include <cstring>
#include <algorithm> // for qsort and bsearch

template <typename T>
class Vector
{
public:
    T* data;
    size_t size;

    Vector(size_t s) : size(s)
    {
        data = new T[size];
    }

    Vector(const T* d, size_t s) : size(s)
    {
        data = new T[size];
        std::memcpy(data, d, size * sizeof(T));
    }

    ~Vector()
    {
        delete[] data;
    }

    Vector operator+(const Vector& other) const
    {
        Vector result(size);
        for (size_t i = 0; i < size; ++i)
        {
            result.data[i] = data[i] + other.data[i];
        }
        return result;
    }

    Vector operator-(const Vector& other) const
    {
        Vector result(size);
        for (size_t i = 0; i < size; ++i)
        {
            result.data[i] = data[i] - other.data[i];
        }
        return result;
    }

    Vector operator*(const Vector& other) const
    {
        Vector result(size);
        for (size_t i = 0; i < size; ++i)
        {
            result.data[i] = data[i] * other.data[i];
        }
        return result;
    }

    Vector operator/(const Vector& other) const
    {
        Vector result(size);
        for (size_t i = 0; i < size; ++i)
        {
            result.data[i] = data[i] / other.data[i];
        }
        return result;
    }

    Vector operator&(const Vector& other) const
    {
        Vector result(size);
        for (size_t i = 0; i < size; ++i)
        {
            result.data[i] = data[i] & other.data[i];
        }
        return result;
    }

    Vector operator|(const Vector& other) const
    {
        Vector result(size);
        for (size_t i = 0; i < size; ++i)
        {
            result.data[i] = data[i] | other.data[i];
        }
        return result;
    }

    Vector operator^(const Vector& other) const
    {
        Vector result(size);
        for (size_t i = 0; i < size; ++i)
        {
            result.data[i] = data[i] ^ other.data[i];
        }
        return result;
    }

    void sort()
    {
        std::qsort(data, size, sizeof(T), [](const void* a, const void* b)
        {
            T arg1 = *static_cast<const T*>(a);
            T arg2 = *static_cast<const T*>(b);
            return (arg1 > arg2) - (arg1 < arg2);
        });
    }

    bool search(T value) const
    {
        return std::bsearch(&value, data, size, sizeof(T), [](const void* a, const void* b)
        {
            T arg1 = *static_cast<const T*>(a);
            T arg2 = *static_cast<const T*>(b);
            return (arg1 > arg2) - (arg1 < arg2);
        }) != nullptr;
    }
};

int main()
{
    int d1[] = {1, 2, 3, 4};
    int d2[] = {5, 6, 7, 8};

    Vector<int> v1(d1, 4);
    Vector<int> v2(d2, 4);

    Vector<int> vAdd = v1 + v2;
    Vector<int> vSub = v1 - v2;
    Vector<int> vMul = v1 * v2;
    Vector<int> vDiv = v1 / v2;

    std::cout << "Addition: ";
    for (size_t i = 0; i < vAdd.size; ++i)
    {
        std::cout << vAdd.data[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Subtraction: ";
    for (size_t i = 0; i < vSub.size; ++i)
    {
        std::cout << vSub.data[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Multiplication: ";
     for (size_t i = 0; i < vMul.size; ++i)
    {
        std::cout << vMul.data[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Division: ";
    for (size_t i = 0; i < vDiv.size; ++i)
    {
        std::cout << vDiv.data[i] << " ";
    }
    std::cout << std::endl;

    Vector<int> vAnd = v1 & v2;
    Vector<int> vOr = v1 | v2;
    Vector<int> vXor = v1 ^ v2;

    std::cout << "Bitwise AND: ";
    for (size_t i = 0; i < vAnd.size; ++i)
    {
        std::cout << vAnd.data[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Bitwise OR: ";
    for (size_t i = 0; i < vOr.size; ++i)
    {
        std::cout << vOr.data[i] << " ";
    }
    std::cout << std::endl;

    std::cout << "Bitwise XOR: ";
    for (size_t i = 0; i < vXor.size; ++i)
    {
        std::cout << vXor.data[i] << " ";
    }
    std::cout << std::endl;

    v1.sort();
    std::cout << "Sorted Vector: ";
    for (size_t i = 0; i < v1.size; ++i)
    {
        std::cout << v1.data[i] << " ";
    }
    std::cout << std::endl;

    int valueToSearch = 3;
    bool found = v1.search(valueToSearch);
    std::cout << "Value " << valueToSearch << " found in vector: " << (found ? "Yes" : "No") << std::endl;

    return 0;
}


