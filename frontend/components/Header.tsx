"use client";

import Link from "next/link";
import { UserProfileModal } from "./UserGroupProfileModal";
import { UserData } from "@/types/UserData";
import { UserButton } from "./UserButton";
import { useState } from "react";
import {useAuth} from "@/contexts/AuthContext";

function Header() {
    const auth = useAuth();
    const [showProfileModal, setShowProfileModal] = useState(false);
    const user = auth.user;
    const userData: UserData | null = user
        ? {
              id: user.id as string,
              email: user.email ?? "",
              name: user.name ?? "User",
          }
        : null;

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
                    <div className="flex items-center gap-2">
                        <UserButton onOpenProfile={() => openProfile()} />
                    </div>
                </div>
            </div>

            {/* Profile Modal */}
            {showProfileModal && userData && (
                console.log("Opening profile modal with user data:", userData),
                <UserProfileModal
                    userData={userData}
                    onClose={() => setShowProfileModal(false)}
                />
            )}
        </header>
    );
}

export default Header;
