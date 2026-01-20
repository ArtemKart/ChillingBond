"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RegisterPage() {
    const [email, setEmail] = useState("");
    const [name, setName] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError("");

        if (password.length < 8) {
            setError("Пароль должен содержать минимум 8 символов");
            return;
        }

        if (password !== confirmPassword) {
            setError("Пароли не совпадают");
            return;
        }

        setLoading(true);

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/users`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        email,
                        name: name.trim() || null,
                        password,
                    }),
                },
            );

            if (!response.ok) {
                let errorMessage = "Registration error";

                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch {
                    errorMessage = `Ошибка ${response.status}: ${response.statusText}`;
                }

                const friendlyMessages: Record<number, string> = {
                    409: errorMessage,
                    422: "Please check that the entered data is correct.\n",
                    400: "Invalid request\n",
                    500: "Server error. Please try again later.\n",
                    503: "Service temporarily unavailable.\n",
                };

                throw new Error(
                    friendlyMessages[response.status] || errorMessage,
                );
            }

            router.push("/login?registered=true");
        } catch (err) {
            if (err instanceof TypeError && err.message.includes("fetch")) {
                setError(
                    "Failed to connect to the server. Please check your internet connection.",
                );
            } else {
                setError(
                    err instanceof Error
                        ? err.message
                        : "An unknown error has occurred.\n",
                );
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50">
            <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
                {/* Header */}
                <div>
                    <h2 className="text-center text-3xl font-bold text-gray-900">
                        Create an account
                    </h2>
                    <p className="mt-2 text-left text-sm text-gray-600">
                        Already have an account?{" "}
                        <Link
                            href="/login"
                            className="font-medium text-blue-600 hover:text-blue-500"
                        >
                            Log in
                        </Link>
                    </p>
                </div>

                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    <div className="space-y-4">
                        <div>
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 placeholder-gray-300 text-gray-900"
                                placeholder="Your email"
                                disabled={loading}
                            />
                        </div>

                        <div>
                            <input
                                id="name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 placeholder-gray-300 text-gray-900"
                                placeholder="Your name"
                                disabled={loading}
                            />
                        </div>

                        <div>
                            <div className="relative">
                                <input
                                    id="password"
                                    type="password"
                                    required
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="mt-1 block w-full px-3 py-2 pr-10 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 placeholder-gray-300 text-gray-900"
                                    placeholder="Your password"
                                    minLength={8}
                                    disabled={loading}
                                />
                                <div
                                    className="absolute inset-y-0 right-0 flex items-center pr-3 cursor-help"
                                    title="At least 8 characters and 1 number"
                                >
                                    <svg
                                        className="h-5 w-5 text-gray-400 hover:text-gray-600"
                                        fill="currentColor"
                                        viewBox="0 0 20 20"
                                    >
                                        <path
                                            fillRule="evenodd"
                                            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z"
                                            clipRule="evenodd"
                                        />
                                    </svg>
                                </div>
                            </div>
                        </div>

                        <div>
                            <input
                                id="confirmPassword"
                                type="password"
                                required
                                value={confirmPassword}
                                onChange={(e) =>
                                    setConfirmPassword(e.target.value)
                                }
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 placeholder-gray-300 text-gray-900"
                                placeholder="Repeat password"
                                minLength={8}
                                disabled={loading}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading ? "Creating..." : "Create"}
                    </button>
                </form>
            </div>
        </div>
    );
}
