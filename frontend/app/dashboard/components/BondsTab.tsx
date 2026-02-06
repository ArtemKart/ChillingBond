"use client";

import { ApiError, apiFetch } from "@/lib/api";
import { BondHolderResponse } from "@/types/Bond";
import { TrendingUp, Users, DollarSign, Package, Currency, Landmark, FolderKanban } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { BondsList } from "./BondsList";
import BondModal from "@/components/BondModal";
import AddBondModal from "@/components/AddBondModal";
import { calculateBondMetrics, formatMetricValue } from "./BondMetrics";
import { fetchTotalMonthlyIncome } from "@/lib/bondCalculations";

export function BondsTab() {
    const router = useRouter();
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    const [selectedBond, setSelectedBond] = useState<BondHolderResponse | null>(
        null,
    );
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [groupByDate, setGroupByDate] = useState(false);
    const [sortBy, setSortBy] = useState("series");
    const [showSortMenu, setShowSortMenu] = useState(false);
    const [bonds, setBonds] = useState<BondHolderResponse[]>([]);

    const [monthlyIncome, setMonthlyIncome] = useState<number>(0);
    const metrics = useMemo(() => {
        return calculateBondMetrics(bonds, monthlyIncome);
    }, [bonds, monthlyIncome]);

    const summaryMetrics = [
        {
            title: "Total Bondholders",
            value: formatMetricValue(
                "totalBondholders",
                metrics.totalBondholders,
            ),
            icon: Users,
            color: "blue",
        },
        {
            title: "Total Investment",
            value: formatMetricValue(
                "totalInvestment",
                metrics.totalInvestment,
            ),
            icon: Landmark,
            color: "green",
        },
        {
            title: "Active Bonds",
            value: formatMetricValue("activeBonds", metrics.activeBonds),
            icon: FolderKanban,
            color: "purple",
        },
        {
            title: "Current Month Income",
            value: formatMetricValue(
                "currentMonthIncome",
                metrics.currentMonthIncome,
            ),
            icon: TrendingUp,
            color: "red",
        },
    ];

    const sortOptions = [
        { value: "series", label: "Series" },
        { value: "quantity", label: "Quantity" },
        { value: "faceValue", label: "Face Value" },
        { value: "totalValue", label: "Total Value" },
        { value: "purchaseDate", label: "Purchase Date" },
    ];

    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
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

    const handleClose = () => {
        setSelectedBond(null);
    };

    const groupedBonds = groupByDate
        ? sortedBonds.reduce(
              (acc, bond) => {
                  const dateKey = new Date(
                      bond.purchase_date,
                  ).toLocaleDateString("ru-RU");
                  if (!acc[dateKey]) {
                      acc[dateKey] = [];
                  }
                  acc[dateKey].push(bond);
                  return acc;
              },
              {} as Record<string, BondHolderResponse[]>,
          )
        : { "All bonds": sortedBonds };

    const loadBonds = async () => {
        try {
            const result = await apiFetch<BondHolderResponse[]>("/bonds");
            setBonds(result);

            if (result.length > 0) {
                const bondholderIds = result.map((bond) => bond.id);
                const income = await fetchTotalMonthlyIncome(bondholderIds);
                setMonthlyIncome(income);
            }
        } catch (err) {
            if (err instanceof ApiError && err.status == 401) {
                router.push("/login");
            }
            setError(err instanceof Error ? err.message : "Loading error");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadBonds();
    }, []);

    const refetch = async () => {
        await loadBonds();
    };

    return (
        <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-6">
                Bonds Overview
            </h2>

            {/* Summary Metrics */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {summaryMetrics.map((metric) => {
                    const Icon = metric.icon;

                    return (
                        <div
                            key={metric.title}
                            className="bg-white rounded-lg border border-gray-200 p-6"
                        >
                            <div className="flex items-center gap-4">
                                <div
                                    className={`p-3 bg-${metric.color}-50 rounded-lg`}
                                >
                                    <Icon
                                        className={`size-6 text-${metric.color}-600`}
                                    />
                                </div>
                                <div>
                                    <p className="text-sm text-gray-600 mb-1">
                                        {metric.title}
                                    </p>
                                    <p className="text-2xl font-semibold text-gray-900">
                                        {metric.value}
                                    </p>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            <BondsList
                bonds={sortedBonds}
                groupedBonds={groupedBonds}
                onBondClick={setSelectedBond}
                onAddClick={() => setIsAddModalOpen(true)}
            />

            {isAddModalOpen && (
                <AddBondModal
                    onClose={() => setIsAddModalOpen(false)}
                    onUpdate={loadBonds}
                />
            )}

            {selectedBond && (
                <BondModal
                    bond={selectedBond}
                    onClose={() => setSelectedBond(null)}
                />
            )}
        </div>
    );
}
