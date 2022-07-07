import React from 'react';

import {
  signup as apiSignup,
  login as apiLogin,
  token as apiToken,
  ACCESS_TOKEN_NAME,
} from '../apiClient';

import { DBUser } from '../types';

interface IAuthContext {
  userDetails: DBUser | null;
  setUserDetails: React.Dispatch<React.SetStateAction<DBUser | null>>;
  signup: (username: string, password: string, role: string) => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}
const AuthContext = React.createContext<IAuthContext>(null!);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [userDetails, setUserDetails] = React.useState<DBUser | null>(null);

  async function signup(
    username: string,
    password: string,
    role: string
  ): Promise<void> {
    const res = await apiSignup(username, password, role);

    await localStorage.removeItem(ACCESS_TOKEN_NAME);
    await localStorage.setItem(ACCESS_TOKEN_NAME, res.token as string);

    setUserDetails(res);
  }

  async function login(username: string, password: string): Promise<void> {
    const formData = new URLSearchParams({
      username,
      password,
    });

    const res = await apiLogin(formData);

    await localStorage.removeItem(ACCESS_TOKEN_NAME);
    await localStorage.setItem(ACCESS_TOKEN_NAME, res.token as string);

    setUserDetails(res);
  }

  async function logout() {
    await localStorage.removeItem(ACCESS_TOKEN_NAME);

    setUserDetails(null);
  }

  React.useEffect(() => {
    if (!userDetails) {
      (async () => {
        const token = await localStorage.getItem(ACCESS_TOKEN_NAME);

        if (!token) {
          return;
        }

        const res = await apiToken();

        if (res.token) {
          setUserDetails(res);
        }
      })();
    }
  }, [userDetails]);

  let value = { userDetails, setUserDetails, signup, login, logout };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return React.useContext(AuthContext);
}

export default AuthProvider;
