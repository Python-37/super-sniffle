# cython: language_level=3
from libc.stdlib cimport free, malloc

from cpython.object cimport PyObject
from cpython.ref cimport Py_INCREF
import numpy as np
cimport numpy as np

np.import_array()


cdef extern from "numpy/arrayobject.h":
    # a little bit awkward: the reference to obj will be stolen
    # using PyObject*  to signal that Cython cannot handle it automatically
    int PyArray_SetBaseObject(np.ndarray arr, PyObject *obj) except -1


ctypedef np.uint8_t uint8
ctypedef fused py_seq:
    list
    tuple


cdef class MemoryNanny:
    cdef void* ptr
    cdef int h, w

    def __cinit__(self, N, img):
        cdef np.npy_intp dims[2]
        dims[0] = N[0]; dims[1] = N[1]
        cdef uint8 *ptr = <uint8*>malloc(sizeof(uint8) * N[0] * N[1]);
        cdef np.ndarray[np.npy_uint8, ndim=2] arr = np.PyArray_SimpleNewFromData(2, dims, np.NPY_UINT8, ptr)
        self.h = N[0]; self.w = N[1]
        self.ptr = ptr
        Py_INCREF(self)
        PyArray_SetBaseObject(arr, <PyObject*>self)
        tmp = np.asarray(arr)
        tmp[...] = img[:, :]
        print(tmp, tmp.shape, tmp.dtype)  # NOTE just debug
        self._get_arr()

    def __dealloc__(self):
        if self.ptr != NULL:
            print("recycling memory")  # NOTE just debug
            free(self.ptr)

    def _get_arr(self):
        cdef np.npy_intp dims[2]
        dims[0] = self.h; dims[1] = self.w
        arr = np.PyArray_SimpleNewFromData(2, dims, np.NPY_UINT8, self.ptr)
        tmp = np.asarray(arr)
        print("get array", tmp, tmp.shape, tmp.dtype)  # NOTE just debug
        return tmp


cpdef void create(py_seq size):
    img = np.random.randint(1, 255, size=size, dtype=np.uint8)  # 随机设定个值
    MemoryNanny(size, img)
