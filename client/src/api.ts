import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface User {
  id: number;
  username: string;
  role: 'student' | 'teacher' | 'admin';
  first_name: string;
  last_name: string;
}

export interface Course {
  id: number;
  course_code: string;
  name: string;
  description?: string;
  instructor: string;
  capacity: number;
  current_enrollment: number;
  is_enrolled?: boolean;
  grade?: number | null;
}

export interface StudentEnrollment {
  id: number;
  course_code: string;
  name: string;
  description?: string;
  instructor: string;
  capacity: number;
  current_enrollment: number;
  grade?: number | null;
}

export interface TeacherCourse {
  id: number;
  course_code: string;
  name: string;
  description?: string;
  capacity: number;
  current_enrollment: number;
}

export interface Student {
  enrollment_id: number;
  student_id: number;
  student_name: string;
  username: string;
  grade: number | null;
}

// Auth API
export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await api.post('/login', { username, password });
    return response.data;
  },
  logout: async () => {
    const response = await api.post('/logout');
    return response.data;
  },
  checkAuth: async () => {
    const response = await api.get('/check-auth');
    return response.data;
  },
};

// Student API
export const studentAPI = {
  getDashboard: async () => {
    const response = await api.get('/student/dashboard');
    return response.data;
  },
  getAllCourses: async () => {
    const response = await api.get('/student/courses');
    return response.data;
  },
  enroll: async (classId: number) => {
    const response = await api.post(`/student/enroll/${classId}`);
    return response.data;
  },
};

// Teacher API
export const teacherAPI = {
  getDashboard: async () => {
    const response = await api.get('/teacher/dashboard');
    return response.data;
  },
  getCourseDetail: async (classId: number) => {
    const response = await api.get(`/teacher/course/${classId}`);
    return response.data;
  },
  updateGrade: async (enrollmentId: number, grade: number | null) => {
    const response = await api.put(`/teacher/grade/${enrollmentId}`, { grade });
    return response.data;
  },
};

export default api;

