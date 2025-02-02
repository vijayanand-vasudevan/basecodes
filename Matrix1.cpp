#include <iostream>
#include <cstring>
#include <algorithm> // for qsort and bsearch

template <typename T>
class Matrix
{
public:
    T* data;
    size_t rows;
    size_t cols;

    Matrix(size_t r, size_t c) : rows(r), cols(c)
    {
        data = new T[rows * cols];
    }

    Matrix(const T* d, size_t r, size_t c) : rows(r), cols(c)
    {
        data = new T[rows * cols];
        std::memcpy(data, d, rows * cols * sizeof(T));
    }

    ~Matrix()
    {
        delete[] data;
    }

    Matrix operator+(const Matrix& other) const
    {
        Matrix result(rows, cols);
        for (size_t i = 0; i < rows * cols; i += 2)
        {
            asm(
                "movupd (%1), %%xmm0\n\t"
                "movupd (%2), %%xmm1\n\t"
                "addpd %%xmm1, %%xmm0\n\t"
                "movupd %%xmm0, (%0)\n\t"
                : 
                : "r"(result.data + i), "r"(data + i), "r"(other.data + i)
                : "%xmm0", "%xmm1"
            );
        }
        return result;
    }

    Matrix operator-(const Matrix& other) const
    {
        Matrix result(rows, cols);
        for (size_t i = 0; i < rows * cols; i += 2)
        {
            asm(
                "movupd (%1), %%xmm0\n\t"
                "movupd (%2), %%xmm1\n\t"
                "subpd %%xmm1, %%xmm0\n\t"
                "movupd %%xmm0, (%0)\n\t"
                : 
                : "r"(result.data + i), "r"(data + i), "r"(other.data + i)
                : "%xmm0", "%xmm1"
            );
        }
        return result;
    }

    Matrix operator*(const Matrix& other) const
    {
        Matrix result(rows, cols);
        for (size_t i = 0; i < rows * cols; i += 2)
        {
            asm(
                "movupd (%1), %%xmm0\n\t"
                "movupd (%2), %%xmm1\n\t"
                "mulpd %%xmm1, %%xmm0\n\t"
                "movupd %%xmm0, (%0)\n\t"
                : 
                : "r"(result.data + i), "r"(data + i), "r"(other.data + i)
                : "%xmm0", "%xmm1"
            );
        }
        return result;
    }

    Matrix operator/(const Matrix& other) const
    {
        Matrix result(rows, cols);
        for (size_t i = 0; i < rows * cols; i += 2)
        {
            asm(
                "movupd (%1), %%xmm0\n\t"
                "movupd (%2), %%xmm1\n\t"
                "divpd %%xmm1, %%xmm0\n\t"
                "movupd %%xmm0, (%0)\n\t"
                : 
                : "r"(result.data + i), "r"(data + i), "r"(other.data + i)
                : "%xmm0", "%xmm1"
            );
        }
        return result;
    }

    Matrix operator&(const Matrix& other) const
    {
        Matrix result(rows, cols);
        for (size_t i = 0; i < rows * cols; ++i)
        {
            result.data[i] = data[i] & other.data[i];
        }
        return result;
    }

    Matrix operator|(const Matrix& other) const
    {
        Matrix result(rows, cols);
        for (size_t i = 0; i < rows * cols; ++i)
        {
            result.data[i] = data[i] | other.data[i];
        }
        return result;
    }

    Matrix operator^(const Matrix& other) const
    {
        Matrix result(rows, cols);
        for (size_t i = 0; i < rows * cols; ++i)
        {
            result.data[i] = data[i] ^ other.data[i];
        }
        return result;
    }

    void sort()
    {
        std::qsort(data, rows * cols, sizeof(T), [](const void* a, const void* b)
        {
            T arg1 = *static_cast<const T*>(a);
            T arg2 = *static_cast<const T*>(b);
            return (arg1 > arg2) - (arg1 < arg2);
        });
    }

    bool search(T value) const
    {
        return std::bsearch(&value, data, rows * cols, sizeof(T), [](const void* a, const void* b)
        {
            T arg1 = *static_cast<const T*>(a);
            T arg2 = *static_cast<const T*>(b);
            return (arg1 > arg2) - (arg1 < arg2);
        }) != nullptr;
    }

    void print() const
    {
        for (size_t i = 0; i < rows; ++i)
        {
            for (size_t j = 0; j < cols; ++j)
            {
                std::cout << data[i * cols + j] << " ";
            }
            std::cout << std::endl;
        }
    }
};

int main()
{
    int32_t d1[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
    int32_t d2[] = {12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1};

    Matrix<int32_t> m1(d1, 3, 4);
    Matrix<int32_t> m2(d2, 3, 4);

    Matrix<int32_t> mAdd = m1 + m2;
    Matrix<int32_t> mSub = m1 - m2;
    Matrix<int32_t> mMul = m1 * m2;
    Matrix<int32_t> mDiv = m1 / m2;

    std::cout << "Addition:" << std::endl;
    mAdd.print();

    std::cout << "Subtraction:" << std::endl;
    mSub.print();

    std::cout << "Multiplication:" << std::endl;
    mMul.print();

    std::cout << "Division:" << std::endl;
    mDiv.print();

    Matrix<int32_t> mAnd = m1 & m2;
    Matrix<int32_t> mOr = m1 | m2;
    Matrix<int32_t> mXor = m1 ^ m2;

    std::cout << "Bitwise AND:" << std::endl;
    mAnd.print();

    std::cout << "Bitwise OR:" << std::endl;
    mOr.print();

    std::cout << "Bitwise XOR:" << std::endl;
    mXor.print();

    m1.sort();
    std::cout << "Sorted Matrix:" << std::endl;
    m1.print();

    int32_t valueToSearch = 3;
    bool found = m1.search(valueToSearch);
    std::cout << "Value " << valueToSearch << " found in matrix: " << (found ? "Yes" : "No") << std::endl;

    return 0;
}
