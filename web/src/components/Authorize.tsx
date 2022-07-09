import React from 'react';
import { Navigate, Link } from 'react-router-dom';
import Typography from '@mui/material/Typography';
import TextField from '@mui/material/TextField';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Button from '@mui/material/Button';
import { useAuth } from './AuthProvider';

import { UserCreate } from '../types';

interface IAuthorize {
  type: 'login' | 'signup';
}

const LoginForm = ({
  action,
}: {
  action: (username: string, password: string) => Promise<void>;
}) => {
  const [username, setUsername] = React.useState<string>('');
  const [password, setPassword] = React.useState<string>('');
  const [error, setError] = React.useState<string>('');

  async function handleClick() {
    setError('');

    if (!username.length || !password.length) {
      setError('Please fill all fields');
      return;
    }

    try {
      await action(username, password);
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <div style={{ maxWidth: 350, margin: '0 auto' }}>
      <Typography variant="h3" align="center" gutterBottom>
        Login
      </Typography>

      <TextField
        id="username"
        label="Username"
        variant="outlined"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ width: '100%', marginBottom: 16 }}
      />

      <TextField
        type="password"
        id="password"
        label="Password"
        variant="outlined"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ width: '100%', marginBottom: 16 }}
      />

      <Button
        variant="contained"
        onClick={handleClick}
        style={{ width: '100%', marginBottom: 16 }}
      >
        Submit
      </Button>

      <Typography variant="body2">
        Don't have an account? <Link to="/signup">Sign up</Link>
      </Typography>

      {error && (
        <Typography variant="body1" style={{ color: 'red' }}>
          {error}
        </Typography>
      )}
    </div>
  );
};

const SignupForm = ({
  action,
}: {
  action: (data: UserCreate) => Promise<void>;
}) => {
  const [username, setUsername] = React.useState<string>('');
  const [password, setPassword] = React.useState<string>('');
  const [role, setRole] = React.useState<string>('');
  const [error, setError] = React.useState<string>('');

  async function handleClick() {
    setError('');

    if (!username.length || !password.length) {
      setError('Please fill all fields');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 chars');
      return;
    }

    if (role === '') {
      setError('You must select a role');
      return;
    }

    try {
      await action({ username, password, role });
    } catch (e: any) {
      setError(e.message);
    }
  }

  return (
    <div style={{ maxWidth: 350, margin: '0 auto' }}>
      <Typography variant="h3" align="center" gutterBottom>
        Signup
      </Typography>

      <TextField
        id="username"
        label="Username"
        variant="outlined"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        style={{ width: '100%', marginBottom: 16 }}
      />

      <TextField
        type="password"
        id="password"
        label="Password"
        variant="outlined"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        style={{ width: '100%', marginBottom: 16 }}
      />

      <Select
        id="role"
        variant="outlined"
        label="Role"
        value={role}
        onChange={(e) => setRole(e.target.value)}
        style={{ width: '100%', marginBottom: 16 }}
      >
        <MenuItem value="buyer">Buyer</MenuItem>
        <MenuItem value="seller">Seller</MenuItem>
      </Select>

      <Button
        variant="contained"
        onClick={handleClick}
        style={{ width: '100%', marginBottom: 16 }}
      >
        Submit
      </Button>

      <Typography variant="body2">
        Already have an account? <Link to="/login">Log in</Link>
      </Typography>

      {error && (
        <Typography variant="body1" style={{ color: 'red' }}>
          {error}
        </Typography>
      )}
    </div>
  );
};

function Authorize({ type }: IAuthorize) {
  const { userDetails, login, signup } = useAuth();

  if (userDetails) {
    return <Navigate to="/" />;
  }

  switch (type) {
    case 'login':
      return <LoginForm action={login} />;
    case 'signup':
      return <SignupForm action={signup} />;
    default:
      return null;
  }
}

export default Authorize;
