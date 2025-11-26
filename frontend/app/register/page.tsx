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
                let errorMessage = "Ошибка регистрации";

                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorMessage;
                } catch {
                    errorMessage = `Ошибка ${response.status}: ${response.statusText}`;
                }

                const friendlyMessages: Record<number, string> = {
                    409: errorMessage,
                    422: "Проверьте правильность введённых данных",
                    400: "Неверный запрос",
                    500: "Ошибка сервера. Попробуйте позже",
                    503: "Сервис временно недоступен",
                };

                throw new Error(
                    friendlyMessages[response.status] || errorMessage,
                );
            }

            router.push("/login?registered=true");
        } catch (err) {
            if (err instanceof TypeError && err.message.includes("fetch")) {
                setError(
                    "Не удалось подключиться к серверу. Проверьте интернет-соединение",
                );
            } else {
                setError(
                    err instanceof Error
                        ? err.message
                        : "Произошла неизвестная ошибка",
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
                        Регистрация
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Уже есть аккаунт?{" "}
                        <Link
                            href="/login"
                            className="font-medium text-blue-600 hover:text-blue-500"
                        >
                            Войти
                        </Link>
                    </p>
                </div>

                {/* Form */}
                <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                    {/* Error Alert */}
                    {error && (
                        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
                            {error}
                        </div>
                    )}

                    <div className="space-y-4">
                        {/* Email Field */}
                        <div>
                            <label
                                htmlFor="email"
                                className="block text-sm font-medium text-gray-700"
                            >
                                Email <span className="text-red-500">*</span>
                            </label>
                            <input
                                id="email"
                                type="email"
                                required
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="your@email.com"
                                disabled={loading}
                            />
                        </div>

                        {/* Name Field (Optional) */}
                        <div>
                            <label
                                htmlFor="name"
                                className="block text-sm font-medium text-gray-700"
                            >
                                Имя{" "}
                                <span className="text-gray-400 text-xs">
                                    (необязательно)
                                </span>
                            </label>
                            <input
                                id="name"
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="Иван Иванов"
                                disabled={loading}
                            />
                        </div>

                        {/* Password Field */}
                        <div>
                            <label
                                htmlFor="password"
                                className="block text-sm font-medium text-gray-700"
                            >
                                Пароль <span className="text-red-500">*</span>
                            </label>
                            <input
                                id="password"
                                type="password"
                                required
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="••••••••"
                                minLength={8}
                                disabled={loading}
                            />
                            <p className="mt-1 text-sm text-gray-500">
                                Минимум 8 символов
                            </p>
                        </div>

                        {/* Confirm Password Field */}
                        <div>
                            <label
                                htmlFor="confirmPassword"
                                className="block text-sm font-medium text-gray-700"
                            >
                                Подтвердите пароль{" "}
                                <span className="text-red-500">*</span>
                            </label>
                            <input
                                id="confirmPassword"
                                type="password"
                                required
                                value={confirmPassword}
                                onChange={(e) =>
                                    setConfirmPassword(e.target.value)
                                }
                                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                                placeholder="••••••••"
                                minLength={8}
                                disabled={loading}
                            />
                        </div>
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                    >
                        {loading ? "Регистрация..." : "Зарегистрироваться"}
                    </button>
                </form>
            </div>
        </div>
    );
}
