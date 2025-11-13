import { useState, useEffect } from 'react';
import { studentAPI, authAPI } from '../api';
import './Dashboard.css';

interface StudentDashboardProps {
  user: any;
  onLogout: () => void;
}

// We don't strictly need strong TypeScript types here for runtime behaviour,
// so we keep things simple and avoid importing types from the API module.
type EnrolledCourse = {
  id: number;
  course_code: string;
  name: string;
  description?: string;
  instructor: string;
  capacity: number;
  current_enrollment: number;
  grade?: number | null;
  is_enrolled?: boolean;
};

type CourseItem = EnrolledCourse;

export default function StudentDashboard({ user, onLogout }: StudentDashboardProps) {
  const [enrolledCourses, setEnrolledCourses] = useState<EnrolledCourse[]>([]);
  const [allCourses, setAllCourses] = useState<CourseItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAllCourses, setShowAllCourses] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [dashboardData, coursesData] = await Promise.all([
        studentAPI.getDashboard(),
        studentAPI.getAllCourses()
      ]);
      setEnrolledCourses(dashboardData.enrolled_courses || []);
      setAllCourses(coursesData.courses || []);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async (classId: number) => {
    try {
      await studentAPI.enroll(classId);
      setError('');
      await loadData(); // Reload data after enrollment
      alert('Successfully enrolled in course!');
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to enroll in course');
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

  const availableCourses = allCourses.filter(course => !course.is_enrolled);

  if (loading) {
    return <div className="dashboard-container"><div className="loading">Loading...</div></div>;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <div>
          <h1>Welcome {user.first_name} {user.last_name}!</h1>
          <p>Student Dashboard</p>
        </div>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-content">
        <section className="courses-section">
          <h2>Your Courses</h2>
          {enrolledCourses.length === 0 ? (
            <p className="empty-state">You are not enrolled in any courses yet.</p>
          ) : (
            <div className="courses-grid">
              {enrolledCourses.map((course) => (
                <div key={course.id} className="course-card">
                  <h3>{course.course_code}</h3>
                  <h4>{course.name}</h4>
                  <p className="instructor">Instructor: {course.instructor}</p>
                  <p className="enrollment">
                    {course.current_enrollment} / {course.capacity} students
                  </p>
                  {course.grade !== null && course.grade !== undefined && (
                    <p className="grade">Grade: {course.grade}%</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="courses-section">
          <div className="section-header">
            <h2>{showAllCourses ? 'All Courses' : 'Available Courses'}</h2>
            <button
              onClick={() => setShowAllCourses(!showAllCourses)}
              className="toggle-button"
            >
              {showAllCourses ? 'Show Available Only' : 'Show All Courses'}
            </button>
          </div>
          {(showAllCourses ? allCourses : availableCourses).length === 0 ? (
            <p className="empty-state">No courses available.</p>
          ) : (
            <div className="courses-grid">
              {(showAllCourses ? allCourses : availableCourses).map((course) => (
                <div key={course.id} className="course-card">
                  <h3>{course.course_code}</h3>
                  <h4>{course.name}</h4>
                  {course.description && <p className="description">{course.description}</p>}
                  <p className="instructor">Instructor: {course.instructor}</p>
                  <p className="enrollment">
                    {course.current_enrollment} / {course.capacity} students
                  </p>
                  {course.is_enrolled ? (
                    <button className="enrolled-button" disabled>
                      Already Enrolled
                    </button>
                  ) : course.current_enrollment >= course.capacity ? (
                    <button className="full-button" disabled>
                      Class Full
                    </button>
                  ) : (
                    <button
                      onClick={() => handleEnroll(course.id)}
                      className="enroll-button"
                    >
                      Enroll
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

