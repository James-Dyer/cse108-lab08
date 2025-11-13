import { useState, useEffect } from 'react';
import { authAPI, teacherAPI } from '../api';
import './Dashboard.css';

interface TeacherDashboardProps {
  user: any;
  onLogout: () => void;
}

// Local view models for the teacher dashboard to avoid depending on runtime
// exports from the shared API types.
type TeacherCourseVM = {
  id: number;
  course_code: string;
  name: string;
  description?: string;
  capacity: number;
  current_enrollment: number;
};

type StudentVM = {
  enrollment_id: number;
  student_id: number;
  student_name: string;
  username: string;
  grade: number | null;
};

export default function TeacherDashboard({ user, onLogout }: TeacherDashboardProps) {
  const [courses, setCourses] = useState<TeacherCourseVM[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<TeacherCourseVM | null>(null);
  const [students, setStudents] = useState<StudentVM[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingStudents, setLoadingStudents] = useState(false);
  const [error, setError] = useState('');
  const [gradeUpdates, setGradeUpdates] = useState<Record<number, number | null>>({});

  useEffect(() => {
    loadCourses();
  }, []);

  const loadCourses = async () => {
    try {
      const data = await teacherAPI.getDashboard();
      setCourses(data.courses || []);
    } catch (err) {
      setError('Failed to load courses');
    } finally {
      setLoading(false);
    }
  };

  const loadCourseDetail = async (classId: number) => {
    setLoadingStudents(true);
    setError('');
    try {
      const data = await teacherAPI.getCourseDetail(classId);
      const course = courses.find((c) => c.id === classId);
      setSelectedCourse(course || null);
      setStudents(data.students || []);
      // Initialize grade updates with current grades
      const grades: Record<number, number | null> = {};
      data.students.forEach((s: StudentVM) => {
        grades[s.enrollment_id] = s.grade;
      });
      setGradeUpdates(grades);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load course details');
    } finally {
      setLoadingStudents(false);
    }
  };

  const handleGradeChange = (enrollmentId: number, value: string) => {
    const grade = value === '' ? null : parseFloat(value);
    if (grade !== null && (isNaN(grade) || grade < 0 || grade > 100)) {
      return; // Invalid grade
    }
    setGradeUpdates({
      ...gradeUpdates,
      [enrollmentId]: grade,
    });
  };

  const handleSaveGrade = async (enrollmentId: number) => {
    const grade = gradeUpdates[enrollmentId];
    try {
      await teacherAPI.updateGrade(enrollmentId, grade);
      setError('');
      // Reload course detail to get updated data
      if (selectedCourse) {
        await loadCourseDetail(selectedCourse.id);
      }
      alert('Grade updated successfully!');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to update grade');
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      onLogout();
    } catch (err) {
      onLogout();
    }
  };

  if (loading) {
    return <div className="dashboard-container"><div className="loading">Loading...</div></div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Welcome Dr. {user.last_name}!</h1>
          <p>Teacher Dashboard</p>
        </div>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-content">
        <section className="courses-section">
          <h2>Your Courses</h2>
          {courses.length === 0 ? (
            <p className="empty-state">You are not teaching any courses yet.</p>
          ) : (
            <div className="courses-grid">
              {courses.map((course) => (
                <div
                  key={course.id}
                  className={`course-card ${selectedCourse?.id === course.id ? 'selected' : ''}`}
                  onClick={() => loadCourseDetail(course.id)}
                  style={{ cursor: 'pointer' }}
                >
                  <h3>{course.course_code}</h3>
                  <h4>{course.name}</h4>
                  <p className="enrollment">
                    {course.current_enrollment} / {course.capacity} students
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>

        {selectedCourse && (
          <section className="courses-section">
            <h2>Students in {selectedCourse.course_code} - {selectedCourse.name}</h2>
            {loadingStudents ? (
              <div className="loading">Loading students...</div>
            ) : students.length === 0 ? (
              <p className="empty-state">No students enrolled in this course.</p>
            ) : (
              <div className="students-table-container">
                <table className="students-table">
                  <thead>
                    <tr>
                      <th>Student Name</th>
                      <th>Username</th>
                      <th>Grade</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {students.map((student) => (
                      <tr key={student.enrollment_id}>
                        <td>{student.student_name}</td>
                        <td>{student.username}</td>
                        <td>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            step="0.1"
                            value={gradeUpdates[student.enrollment_id] ?? ''}
                            onChange={(e) => handleGradeChange(student.enrollment_id, e.target.value)}
                            placeholder="No grade"
                            className="grade-input"
                          />
                        </td>
                        <td>
                          <button
                            onClick={() => handleSaveGrade(student.enrollment_id)}
                            className="save-grade-button"
                            disabled={
                              gradeUpdates[student.enrollment_id] === student.grade
                            }
                          >
                            Save
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}
      </div>
    </div>
  );
}

