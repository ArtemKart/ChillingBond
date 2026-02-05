"use client";

import Link from "next/link";
import { useAuth } from "../contexts/AuthContext";
import { User } from "lucide-react";
import { usePathname } from 'next/navigation';

export default function Header() {
    const { isAuthenticated, logout } = useAuth();
    
    const pathname = usePathname();
    const isDashboard = pathname === '/dashboard';

    const handleLogout = async () => {
        await logout();
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

                    <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg">
                        <User className="size-5" />
                    </button>
                </div>
            </div>
        </header>
    );
}
