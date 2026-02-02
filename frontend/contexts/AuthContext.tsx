"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
    getCurrentUser,
    login as apiLogin,
    logout as apiLogout,
} from "@/lib/api";

type User = {
    id: string;
    username: string;
};

type AuthContextType = {
    isAuthenticated: boolean | null;
    user: User | null;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * AuthProvider initializes auth state on mount and provides
 * helper methods to login/logout and access current user auth state.
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(
        null,
    );
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        let cancelled = false;

        (async () => {
            try {
                const u = await getCurrentUser();
                if (!cancelled) {
                    setUser(u as User);
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
        // Call API login endpoint; apiLogin throws on failure.
        await apiLogin({ username, password });
        // After successful login, refresh current user
        try {
            const u = await getCurrentUser();
            setUser(u as User);
            setIsAuthenticated(true);
        } catch {
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    const logout = async () => {
        try {
            await apiLogout();
        } finally {
            // Always clear local state even if API call fails
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, user, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

/**
 * Hook to access authentication context.
 * Throws if used outside of AuthProvider to fail fast.
 */
export function useAuth(): AuthContextType {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return ctx;
}

export default AuthProvider;
