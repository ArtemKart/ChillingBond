"use client";

import { useEffect, useState } from "react";
import { fetchWithAuth } from "@/lib/api";
import type { BondHolderResponse } from "@/types/bond";
import BondModal from "@/components/BondModal";
import AddBondModal from "@/components/AddBondModal";
import Link from "next/link";
import { DashboardHeader } from "./components/DashboardHeader";
import { SortControls } from "./components/SortControls";
import { BondsList } from "./components/BondsList";
import { Sidebar } from "@/components/Sidebar";

export default function Dashboard() {
    const [bonds, setBonds] = useState<BondHolderResponse[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [selectedBond, setSelectedBond] = useState<BondHolderResponse | null>(
        null,
    );
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [sortBy, setSortBy] = useState<"purchase_date" | "current_value">(
        "purchase_date",
    );
    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const sortedBonds = [...bonds].sort((a, b) => {
        let compareValue = 0;

        if (sortBy === "purchase_date") {
            compareValue =
                new Date(a.purchase_date).getTime() -
                new Date(b.purchase_date).getTime();
        } else if (sortBy === "current_value") {
            const valueA = a.quantity * a.nominal_value;
            const valueB = b.quantity * b.nominal_value;
            compareValue = valueA - valueB;
        }

        return sortOrder === "asc" ? compareValue : -compareValue;
    });

    const groupedBonds = sortedBonds.reduce(
        (acc, bond) => {
            const dateKey = new Date(bond.purchase_date).toLocaleDateString(
                "ru-RU",
            );
            if (!acc[dateKey]) {
                acc[dateKey] = [];
            }
            acc[dateKey].push(bond);
            return acc;
        },
        {} as Record<string, BondHolderResponse[]>,
    );

    const loadBonds = async () => {
        try {
            const response = await fetchWithAuth("/bonds");

            if (!response.ok) {
                throw new Error("Не удалось загрузить облигации");
            }

            const result = await response.json();
            setBonds(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Ошибка загрузки");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadBonds();
    }, []);

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("token_type");
        window.location.href = "/login";
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-gray-600">Загрузка...</div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-gray-50">
                <div className="text-red-600">{error}</div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex">
            <div className="flex-1 p-8">
                <DashboardHeader
                    onAddClick={() => setIsAddModalOpen(true)}
                    onLogout={handleLogout}
                />

                <BondsList
                    bonds={sortedBonds}
                    groupedBonds={groupedBonds}
                    onBondClick={setSelectedBond}
                />
            </div>

            <Sidebar
                isOpen={isSidebarOpen}
                onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
                sortBy={sortBy}
                sortOrder={sortOrder}
                onSortChange={(newSortBy, newSortOrder) => {
                    setSortBy(newSortBy);
                    setSortOrder(newSortOrder);
                }}
            />

            {selectedBond && (
                <BondModal
                    bond={selectedBond}
                    onClose={() => setSelectedBond(null)}
                    onUpdate={loadBonds}
                />
            )}
            {isAddModalOpen && (
                <AddBondModal
                    onClose={() => setIsAddModalOpen(false)}
                    onUpdate={loadBonds}
                />
            )}
        </div>
    );
}
