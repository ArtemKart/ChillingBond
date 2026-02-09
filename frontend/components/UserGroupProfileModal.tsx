import { X, User, Mail, Calendar, Shield } from "lucide-react";
import { UserData } from "@/types/UserData";

interface UserProfileModalProps {
    userData: UserData;
    onClose: () => void;
}

export function UserProfileModal({ userData, onClose }: UserProfileModalProps) {
    return (
        <div
            className="fixed inset-0 flex items-center justify-center z-50 p-4 backdrop-blur-sm bg-black/10"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <h2 className="text-2xl font-semibold text-gray-900">
                        User Profile
                    </h2>
                    <button
                        onClick={onClose}
                        className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg"
                    >
                        <X className="size-5" />
                    </button>
                </div>

                {/* Content */}
                <div className="p-6">
                    {/* Profile Header */}
                    <div className="flex items-center gap-4 mb-6 pb-6 border-b border-gray-200">
                        <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="size-10 text-blue-600" />
                        </div>
                        <div>
                            <h3 className="text-xl font-semibold text-gray-900">
                                {userData.name}
                            </h3>
                            <p className="text-sm text-gray-500">
                                Bond Portfolio Manager
                            </p>
                        </div>
                    </div>

                    {/* Personal Information */}
                    <div className="space-y-4">
                        <h4 className="font-semibold text-gray-900 mb-4">
                            Personal Information
                        </h4>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-gray-50 rounded-lg p-4 md:col-span-2">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="p-2 bg-blue-100 rounded-lg">
                                        <User className="size-4 text-blue-600" />
                                    </div>
                                    <span className="text-sm text-gray-600">
                                        Full Name
                                    </span>
                                </div>
                                <p className="text-base font-medium text-gray-900">
                                    {userData.name}
                                </p>
                            </div>
                            <div className="bg-gray-50 rounded-lg p-4 md:col-span-2">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="p-2 bg-green-100 rounded-lg">
                                        <Mail className="size-4 text-green-600" />
                                    </div>
                                    <span className="text-sm text-gray-600">
                                        Email Address
                                    </span>
                                </div>
                                <p className="text-base font-medium text-gray-900">
                                    {userData.email}
                                </p>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="p-2 bg-purple-100 rounded-lg">
                                        <Calendar className="size-4 text-purple-600" />
                                    </div>
                                    <span className="text-sm text-gray-600">
                                        Member Since
                                    </span>
                                </div>
                                <p className="text-base font-medium text-gray-900">
                                    January 2024
                                </p>
                            </div>

                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center gap-3 mb-2">
                                    <div className="p-2 bg-orange-100 rounded-lg">
                                        <Shield className="size-4 text-orange-600" />
                                    </div>
                                    <span className="text-sm text-gray-600">
                                        Account Status
                                    </span>
                                </div>
                                <span className="inline-flex px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">
                                    Active
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 pt-6 mt-6 border-t border-gray-200">
                        <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                            Edit Profile
                        </button>
                        <button className="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium">
                            Change Password
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
