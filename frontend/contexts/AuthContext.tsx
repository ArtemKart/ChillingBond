"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
    getCurrentUser,
    login as apiLogin,
    logout as apiLogout,
} from "@/lib/api";
import { UserData } from "@/types/UserData";

type AuthContextType = {
    isAuthenticated: boolean | null;
    user: UserData | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    refreshUser: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(
        null,
    );
    const [user, setUser] = useState<UserData | null>(null);

    const refreshUser = async () => {
        try {
            const fullUser = await getCurrentUser();
            setUser(fullUser);
            setIsAuthenticated(true);
        } catch {
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    useEffect(() => {
        let cancelled = false;

        (async () => {
            try {
                const fullUser = await getCurrentUser();
                if (!cancelled) {
                    setUser(fullUser);
                    setIsAuthenticated(true);
                }
            } catch {
                if (!cancelled) {
                    setUser(null);
                    setIsAuthenticated(false);
                }
            }
        })();

        return () => {
            cancelled = true;
        };
    }, []);

    const login = async (username: string, password: string) => {
        await apiLogin({ username, password });
        await refreshUser();
    };

    const logout = async () => {
        try {
            await apiLogout();
        } finally {
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    return (
        <AuthContext.Provider
            value={{ isAuthenticated, user, login, logout, refreshUser }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth(): AuthContextType {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return ctx;
}

export default AuthProvider;
