"use client";

import Link from "next/link";
import { useAuth } from "../contexts/AuthContext";

export default function Header() {
    const { isAuthenticated, logout } = useAuth();

    const handleLogout = async () => {
        await logout();
    };

    return (
        <header className="bg-white shadow-sm sticky top-0 z-10">
            <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    {/* Logo */}
                    <div className="flex items-center">
                        <Link
                            href="/"
                            className="text-2xl font-bold text-blue-600"
                        >
                            ChillingBond
                        </Link>
                    </div>

                    {/* Navigation */}
                    <div className="hidden md:flex items-center space-x-8">
                        <Link
                            href="/dashboard"
                            className="text-gray-700 hover:text-blue-600 font-medium"
                        >
                            Dashboard
                        </Link>
                        <Link
                            href="/about"
                            className="text-gray-700 hover:text-blue-600 font-medium"
                        >
                            About
                        </Link>
                    </div>

                    {/* Auth buttons */}
                    <div className="flex items-center space-x-4">
                        {isAuthenticated === true ? (
                            <button
                                onClick={handleLogout}
                                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
                            >
                                Logout
                            </button>
                        ) : (
                            <>
                                <Link
                                    href="/login"
                                    className="text-gray-700 hover:text-blue-600 font-medium"
                                >
                                    Login
                                </Link>
                                <Link
                                    href="/register"
                                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition font-medium"
                                >
                                    Register
                                </Link>
                            </>
                        )}
                    </div>
                </div>
            </nav>
        </header>
    );
}
