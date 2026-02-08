"use client";

import React, { useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth } from "../contexts/AuthContext";
import { UserButton, UserData } from "./UserButton";

/**
 * Main Header component.
 * This integrates the new UI (title + centered layout + UserButton) but preserves
 * the existing behavior:
 * - Uses the existing AuthContext to determine authentication state and to logout.
 * - Hides the Dashboard link when already on /dashboard (as before).
 * - Keeps the site title linking to root.
 *
 * We export default to keep compatibility with existing imports.
 */
function Header() {
    const auth = useAuth();
    const pathname = usePathname();
    const router = useRouter();

    // Refresh auth state when pathname changes (e.g., after login redirect)
    useEffect(() => {
        if (auth.refreshUser) {
            auth.refreshUser();
        }
    }, [pathname]);

    // old code used "isAuthenticated" and "logout"
    const isAuthenticated = Boolean(auth.isAuthenticated ?? auth.user != null);
    const logout = auth.logout ?? (async () => {});

    // try to derive user data if available
    const user = auth.user;
    const userData: UserData | null = user
        ? {
              firstName: "",
              lastName: "",
              email: user.email ?? "",
              name: user.name,
          }
        : null;

    const isDashboard = pathname === "/dashboard";

    const openProfile = () => {
        // prefer a profile route, fallback to /dashboard if none
        router.push("/profile");
    };

    return (
        <header className="bg-white border-b border-gray-200">
            <div className="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex items-center justify-between h-16">
                    <Link href="/" className="text-2xl font-bold text-blue-600">
                        <h1 className="text-xl font-semibold text-blue-600">
                            ChillingBond
                        </h1>
                    </Link>

                    {!isDashboard && (
                        <div className="hidden md:flex items-center space-x-8">
                            <Link
                                href="/dashboard"
                                className="text-gray-700 hover:text-blue-600 font-medium"
                            >
                                Dashboard
                            </Link>
                        </div>
                    )}

                    <div className="flex items-center gap-2">
                        <UserButton
                            isLoggedIn={isAuthenticated}
                            userData={userData}
                            onLogout={async () => {
                                await logout();
                            }}
                            onOpenProfile={() => openProfile()}
                        />
                    </div>
                </div>
            </div>
        </header>
    );
}

export default Header;
