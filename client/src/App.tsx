import { useState, useEffect } from 'react';
import Login from './components/Login';
import StudentDashboard from './components/StudentDashboard';
import TeacherDashboard from './components/TeacherDashboard';
import { authAPI } from './api';
import './App.css';

// Local User type to avoid runtime imports of types from the API module.
type User = {
  id: number;
  username: string;
  role: 'student' | 'teacher' | 'admin';
  first_name: string;
  last_name: string;
};

// Helper to normalize user object coming from the backend
function normalizeUser(rawUser: any): User {
  const role = (rawUser.role || '').toString().toLowerCase();
  return {
    id: rawUser.id,
    username: rawUser.username,
    role: role === 'student' || role === 'teacher' || role === 'admin' ? role : 'student',
    first_name: rawUser.first_name ?? '',
    last_name: rawUser.last_name ?? '',
  };
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const data = await authAPI.checkAuth();
      if (data.authenticated && data.user) {
        setUser(normalizeUser(data.user));
      }
    } catch (err) {
      // Not authenticated
    } finally {
      setLoading(false);
    }
  };

  const handleLoginSuccess = (loggedInUser: User) => {
    setUser(normalizeUser(loggedInUser));
  };

  const handleLogout = () => {
    setUser(null);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <div>Loading...</div>
      </div>
    );
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />;
  }

  // Admin users should be redirected to Flask-Admin
  if (user.role === 'admin') {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <h1>Admin Dashboard</h1>
        <p>Welcome, {user.first_name} {user.last_name}!</p>
        <p>You are logged in as an administrator.</p>
        <div style={{ marginTop: '2rem' }}>
          <a 
            href="/admin" 
            target="_blank"
            style={{
              display: 'inline-block',
              padding: '1rem 2rem',
              background: '#667eea',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              marginRight: '1rem'
            }}
          >
            Open Admin Panel
          </a>
          <button
            onClick={async () => {
              await authAPI.logout();
              handleLogout();
            }}
            style={{
              padding: '1rem 2rem',
              background: '#e74c3c',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontWeight: '600',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
        <p style={{ marginTop: '2rem', color: '#666' }}>
          The Admin Panel provides full CRUD operations for Users, Classes, and Enrollments.
        </p>
      </div>
    );
  }

  if (user.role === 'student') {
    return <StudentDashboard user={user} onLogout={handleLogout} />;
  }

  if (user.role === 'teacher') {
    return <TeacherDashboard user={user} onLogout={handleLogout} />;
  }

  return <Login onLoginSuccess={handleLoginSuccess} />;
}

export default App;
