"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "../contexts/AuthContext";
import { UserProfileModal } from "./UserGroupProfileModal";
import { UserData } from "@/types/UserData";
import { UserButton } from "./UserButton";

function Header() {
    const auth = useAuth();
    const pathname = usePathname();
    const [showProfileModal, setShowProfileModal] = useState(false);

    useEffect(() => {
        if (auth.refreshUser) {
            auth.refreshUser();
        }
    }, [pathname]);

    const user = auth.user;
    const userData: UserData | null = user
        ? {
              id: user.id as string,
              email: user.email ?? "",
              name: user.name ?? "User",
          }
        : null;

    const isDashboard = pathname === "/dashboard";

    const openProfile = () => {
        setShowProfileModal(true);
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
                        <UserButton onOpenProfile={() => openProfile()} />
                    </div>
                </div>
            </div>

            {/* Profile Modal */}
            {showProfileModal && userData && (
                <UserProfileModal
                    userData={userData}
                    onClose={() => setShowProfileModal(false)}
                />
            )}
        </header>
    );
}

export default Header;
