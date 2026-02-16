"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getCurrentUser, logout } from "@/lib/api";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

export default function HomePage() {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(
        null,
    );
    const data = [
        { month: "Jan", value: 12000 },
        { month: "Feb", value: 13500 },
        { month: "Mar", value: 12800 },
        { month: "Apr", value: 15000 },
        { month: "May", value: 16500 },
        { month: "Jun", value: 17200 },
    ];

    useEffect(() => {
        let cancelled = false;

        (async () => {
            try {
                await getCurrentUser();
                if (!cancelled) setIsAuthenticated(true);
            } catch {
                if (!cancelled) setIsAuthenticated(false);
            }
        })();

        return () => {
            cancelled = true;
        };
    }, []);

    const handleLogout = async () => {
        try {
            await logout();
        } finally {
            window.location.href = "/";
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
            {/* Hero Section */}
            <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                <div className="text-center">
                    <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                        Manage your
                        <span className="text-blue-600"> bonds </span> in a one
                        place
                    </h1>
                    <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                        Track yields, analyze investments, and receive
                        notifications about bond payments. Everything you need
                        for effective bond management.
                    </p>
                    <div className="flex justify-center gap-4">
                        <Link
                            href="/register"
                            className="bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition text-lg font-semibold shadow-lg"
                        >
                            Start for free
                        </Link>
                        <Link
                            href="/dashboard"
                            className="bg-white text-blue-600 px-8 py-4 rounded-lg hover:bg-gray-50 transition text-lg font-semibold border-2 border-blue-600"
                        >
                            Go to dashboard
                        </Link>
                    </div>
                </div>

                <div className="mt-16 bg-white rounded-xl shadow-2xl p-8 border border-gray-200">
                    <div className="aspect-video bg-gradient-to-br from-blue-100 to-blue-50 rounded-lg p-4">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data}>
                                <defs>
                                    <linearGradient
                                        id="colorValue"
                                        x1="0"
                                        y1="0"
                                        x2="0"
                                        y2="1"
                                    >
                                        <stop
                                            offset="5%"
                                            stopColor="#3B82F6"
                                            stopOpacity={0.4}
                                        />
                                        <stop
                                            offset="95%"
                                            stopColor="#3B82F6"
                                            stopOpacity={0}
                                        />
                                    </linearGradient>
                                </defs>

                                <XAxis dataKey="month" />
                                <YAxis />
                                <Tooltip />

                                <Area
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#3B82F6"
                                    strokeWidth={3}
                                    fillOpacity={1}
                                    fill="url(#colorValue)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </section>

            {/* Features Section */}
            <section className="bg-white py-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
                        Key features
                    </h2>

                    <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                        {/* Feature 1 */}
                        <div className="bg-blue-50 rounded-xl p-6 hover:shadow-lg transition">
                            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
                                <span className="text-2xl">📈</span>
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                Bond Tracking
                            </h3>
                            <p className="text-gray-600">
                                Add bonds to your portfolio and track their
                                current value in real time.
                            </p>
                        </div>

                        {/* Feature 2 */}
                        <div className="bg-green-50 rounded-xl p-6 hover:shadow-lg transition">
                            <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
                                <span className="text-2xl">💰</span>
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                Yield Analysis
                            </h3>
                            <p className="text-gray-600">
                                Calculate current yields, forecast future
                                payments, and optimize your portfolio.
                            </p>
                        </div>

                        {/* Feature 3 */}
                        <div className="bg-purple-50 rounded-xl p-6 hover:shadow-lg transition">
                            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
                                <span className="text-2xl">📝</span>
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                Transaction History
                            </h3>
                            <p className="text-gray-600">
                                Keep a complete history of bond purchases,
                                sales, and receipts for tax reporting purposes.
                            </p>
                        </div>

                        {/* Feature 4 */}
                        <div className="bg-orange-50 rounded-xl p-6 hover:shadow-lg transition">
                            <div className="w-12 h-12 bg-orange-600 rounded-lg flex items-center justify-center mb-4">
                                <span className="text-2xl">🔔</span>
                            </div>
                            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                Payment Notifications
                            </h3>
                            <p className="text-gray-600">
                                Receive reminders about upcoming bond payments
                                and bond maturities.
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            {/* How it works Section */}
            <section className="py-20">
                <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
                    <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
                        How it works
                    </h2>

                    <div className="space-y-12">
                        {/* Step 1 */}
                        <div className="flex items-start gap-6">
                            <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
                                1
                            </div>
                            <div>
                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                                    Register
                                </h3>
                                <p className="text-gray-600 text-lg">
                                    Create a free account in 30 seconds. No
                                    complicated forms or verifications.
                                </p>
                            </div>
                        </div>

                        {/* Step 2 */}
                        <div className="flex items-start gap-6">
                            <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
                                2
                            </div>
                            <div>
                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                                    Add Bonds
                                </h3>
                                <p className="text-gray-600 text-lg">
                                    Enter your bond information: series,
                                    quantity, and purchase date. The system will
                                    automatically calculate all metrics.
                                </p>
                            </div>
                        </div>

                        {/* Step 3 */}
                        <div className="flex items-start gap-6">
                            <div className="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center text-xl font-bold">
                                3
                            </div>
                            <div>
                                <h3 className="text-2xl font-semibold text-gray-900 mb-2">
                                    Portfolio Tracking
                                </h3>
                                <p className="text-gray-600 text-lg">
                                    Monitor yields, access analytics, and
                                    receive notifications. Everything you need
                                    for successful investing in one place.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="mt-12 text-center">
                        <Link
                            href="/register"
                            className="inline-block bg-blue-600 text-white px-8 py-4 rounded-lg hover:bg-blue-700 transition text-lg font-semibold"
                        >
                            Try now →
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="bg-gray-900 text-white py-12">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Column 1 */}
                        <div>
                            <h3 className="text-xl font-bold mb-4">
                                ChillingBond
                            </h3>
                            <p className="text-gray-400">
                                A modern tool for managing your bond portfolio
                            </p>
                        </div>

                        {/* Column 2 */}
                        <div>
                            <h4 className="font-semibold mb-4">Links</h4>
                            <ul className="space-y-2">
                                <li>
                                    <Link
                                        href="/"
                                        className="text-gray-400 hover:text-white"
                                    >
                                        Home
                                    </Link>
                                </li>
                                <li>
                                    <Link
                                        href="/dashboard"
                                        className="text-gray-400 hover:text-white"
                                    >
                                        Dashboard
                                    </Link>
                                </li>
                                <li>
                                    <Link
                                        href="/about"
                                        className="text-gray-400 hover:text-white"
                                    >
                                        About
                                    </Link>
                                </li>
                            </ul>
                        </div>

                        {/* Column 3 */}
                        <div>
                            <h4 className="font-semibold mb-4">Contact</h4>
                            <ul className="space-y-2 text-gray-400">
                                <li>
                                    <a
                                        href="mailto:info@chillingbond.com"
                                        className="hover:text-white"
                                    >
                                        info@chillingbond.com
                                    </a>
                                </li>
                                <li>
                                    <Link
                                        href="/privacy"
                                        className="hover:text-white"
                                    >
                                        Privacy Policy
                                    </Link>
                                </li>
                                <li className="flex gap-4 mt-4">
                                    <a href="#" className="hover:text-white">
                                        Telegram
                                    </a>
                                    <a href="#" className="hover:text-white">
                                        GitHub
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>

                    <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
                        <p>&copy; 2025 ChillingBond. All rights reserved.</p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
