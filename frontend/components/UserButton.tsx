"use client";

import { User, LogOut, UserCircle } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import { useRouter } from "next/navigation";
import { UserData } from "@/types/UserData";

interface UserButtonProps {
    isLoggedIn: boolean;
    userData: UserData | null;
    onLogout: () => void;
    onOpenProfile: () => void;
}

export function UserButton({
    isLoggedIn,
    userData,
    onLogout,
    onOpenProfile,
}: UserButtonProps) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);
    const router = useRouter();

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        if (isOpen) {
            document.addEventListener("mousedown", handleClickOutside);
        }

        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [isOpen]);

    const handleLogout = () => {
        onLogout();
        setIsOpen(false);
        router.push("/");
    };

    const handleViewProfile = () => {
        setIsOpen(false);
        onOpenProfile();
    };

    const handleLoginRedirect = () => {
        router.push("/login");
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg"
                onClick={() => setIsOpen(!isOpen)}
            >
                <User className="size-5" />
            </button>

            {isOpen && (
                <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
                    {!isLoggedIn ? (
                        <div className="p-4">
                            <button
                                onClick={handleLoginRedirect}
                                className="w-full flex items-center justify-center gap-2 px-4 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700"
                            >
                                Login
                            </button>
                        </div>
                    ) : (
                        <div className="py-2">
                            <div className="px-4 py-3 border-b border-gray-200">
                                <p className="text-sm font-medium text-gray-900">
                                    {userData?.name || "User"}
                                </p>
                            </div>
                            <button
                                onClick={handleViewProfile}
                                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                            >
                                <UserCircle className="size-4" />
                                View Profile
                            </button>
                            <button
                                onClick={handleLogout}
                                className="w-full flex items-center gap-3 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                            >
                                <LogOut className="size-4" />
                                Logout
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

export type { UserData };
