import React from 'react';

import {
  signup as apiSignup,
  login as apiLogin,
  token as apiToken,
  ACCESS_TOKEN_NAME,
} from '../apiClient';

import { User, UserCreate } from '../types';

interface IAuthContext {
  userDetails: User | null;
  setUserDetails: React.Dispatch<React.SetStateAction<User | null>>;
  signup: (data: UserCreate) => Promise<void>;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}
const AuthContext = React.createContext<IAuthContext>(null!);

function AuthProvider({ children }: { children: React.ReactNode }) {
  const [userDetails, setUserDetails] = React.useState<User | null>(null);

  async function signup(data: UserCreate): Promise<void> {
    const res = await apiSignup(data);

    await localStorage.removeItem(ACCESS_TOKEN_NAME);
    await localStorage.setItem(ACCESS_TOKEN_NAME, res.access_token as string);

    setUserDetails(res);
  }

  async function login(username: string, password: string): Promise<void> {
    const formData = new URLSearchParams({
      username,
      password,
    });

    const res = await apiLogin(formData);

    await localStorage.removeItem(ACCESS_TOKEN_NAME);
    await localStorage.setItem(ACCESS_TOKEN_NAME, res.access_token as string);

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

        if (res.access_token) {
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
